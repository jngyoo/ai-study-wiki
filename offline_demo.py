#!/usr/bin/env python3
"""Mac offline demonstration. Temporarily disables Wi-Fi and restores it in finally.

Run only when the user has authorized the brief network interruption.
The transcript and asciicast contain actual subprocess output, not simulated results.
"""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import signal
import socket
import subprocess
import sys
import time
import threading
from studywiki.core import ROOT, stamp, save_json, read_json


def capture(command):
    r = subprocess.run(command, capture_output=True, text=True, timeout=15)
    return r.stdout.strip(), r.returncode


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--disconnect-wifi', required=True, help='Verified Wi-Fi device, e.g. en0')
    args = parser.parse_args()
    device = args.disconnect_wifi
    before, code = capture(['networksetup', '-getairportpower', device])
    if code or not before.endswith(': On'):
        raise SystemExit('Expected Wi-Fi to be on; refusing to change an unknown state: ' + before)
    service_before, code = capture(['networksetup','-getnetworkserviceenabled','Wi-Fi'])
    if code or service_before != 'Enabled':
        raise SystemExit('Expected the Wi-Fi service to be enabled; refusing to change an unknown state.')
    folder = ROOT / 'evidence/offline' / stamp()
    folder.mkdir(parents=True)
    started = time.monotonic()
    transcript = (folder / 'terminal.txt').open('w')
    recording = (folder / 'terminal.cast').open('w')
    recording.write(json.dumps({'version': 2, 'width': 110, 'height': 36, 'timestamp': int(time.time()),
                                'title': 'AI Study Wiki — actual disconnected local run'}) + '\n')
    def emit(text):
        print(text, end='', flush=True)
        transcript.write(text); transcript.flush()
        recording.write(json.dumps([round(time.monotonic()-started, 3), 'o', text.replace('\n','\r\n')]) + '\n'); recording.flush()
    def run(command, input_text=None, timeout=240):
        import threading
        emit('\n$ ' + ' '.join(command) + '\n')
        process = subprocess.Popen(command, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                   stdin=subprocess.PIPE if input_text else subprocess.DEVNULL, text=True, bufsize=1)
        timer = threading.Timer(timeout, process.kill); timer.start()
        if input_text:
            emit('Input supplied to the CLI:\n' + input_text + '\n')
            process.stdin.write(input_text); process.stdin.close()
        try:
            for line in process.stdout: emit(line)
            rc = process.wait()
        finally:
            timer.cancel()
        emit('[exit ' + str(rc) + ']\n')
        if rc: raise RuntimeError('Command failed; actual output preserved: ' + ' '.join(command))
    def state(label):
        power, _ = capture(['networksetup','-getairportpower',device])
        service, _ = capture(['networksetup','-getnetworkserviceenabled','Wi-Fi'])
        nwi, _ = capture(['scutil','--nwi'])
        active = [x.strip() for x in nwi.splitlines() if x.startswith('Network interfaces:')]
        probes = []
        for address, port in [('1.1.1.1',443),('8.8.8.8',53)]:
            try:
                with socket.create_connection((address,port),timeout=1): pass
                probes.append({'address':address,'connected':True})
            except OSError as e: probes.append({'address':address,'connected':False,'error':str(e)})
        result={'time_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'wifi_power':power,'wifi_service':service,
                'active_network_interfaces':active,'external_connectivity_probes':probes}
        save_json(folder/(label+'.json'),result)
        emit(label + ': ' + json.dumps(result) + '\n')
        return service == 'Disabled' and not active and all(not x['connected'] for x in probes)
    # Backup restoration even if the parent is terminated unexpectedly.
    watchdog = subprocess.Popen([sys.executable,'-c',
        'import time,subprocess;time.sleep(600);subprocess.run(["networksetup","-setnetworkserviceenabled","Wi-Fi","on"]);subprocess.run(["networksetup","-setairportpower",'+repr(device)+',"on"])'],
        start_new_session=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    result = {'started_at':stamp(),'status':'started','original_wifi_state':before}
    stop_monitor = threading.Event()
    samples = []
    monitor = None
    def monitor_network():
        while not stop_monitor.is_set():
            power, rc = capture(['networksetup','-getairportpower',device])
            service, service_rc = capture(['networksetup','-getnetworkserviceenabled','Wi-Fi'])
            nwi, _ = capture(['scutil','--nwi'])
            active = [x.strip() for x in nwi.splitlines() if x.startswith('Network interfaces:')]
            samples.append({'elapsed_seconds':round(time.monotonic()-started,3),
                            'wifi_power':power,'wifi_service':service,'active_interfaces':active,
                            'disconnected':service_rc==0 and service=='Disabled' and not active})
            stop_monitor.wait(1)
    def interrupted(signum, frame): raise KeyboardInterrupt()
    signal.signal(signal.SIGTERM, interrupted)
    try:
        emit('AI Study Wiki: disconnected-internet demonstration\n')
        emit('Each CLI command below starts a new process after Wi-Fi is disabled.\n')
        subprocess.run(['networksetup','-setnetworkserviceenabled','Wi-Fi','off'],check=True,timeout=15)
        subprocess.run(['networksetup','-setairportpower',device,'off'],check=True,timeout=15)
        time.sleep(2)
        if not state('network-before-tests'):
            raise RuntimeError('Could not establish disconnection. No offline success will be claimed.')
        monitor = threading.Thread(target=monitor_network,daemon=True)
        monitor.start()
        run([sys.executable,'wiki.py','--help'])
        run([sys.executable,'wiki.py','doctor'])
        run([sys.executable,'wiki.py','ingest','vault/raw','--force','--only-source','class2'])
        before_notes = {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'vault/wiki').rglob('*.md')}
        run([sys.executable,'wiki.py','ingest','vault/raw'])
        after_notes = {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'vault/wiki').rglob('*.md')}
        result['reingestion_identical'] = before_notes == after_notes
        result['note_count'] = len(after_notes)
        emit('Re-ingestion preserves note paths and contents: '+str(result['reingestion_identical'])+'\n')
        run([sys.executable,'evaluate.py'])
        evaluation = sorted((ROOT/'evidence/evaluations').glob('*/summary.json'))[-1]
        result['evaluation'] = evaluation.relative_to(ROOT).as_posix()
        summary = read_json(evaluation)
        result['all_evaluation_checks_passed'] = all(all(x['checks'].values()) for x in summary['questions']) and all(summary['mode_checks'].values())
        run([sys.executable,'wiki.py','chat'], 'What can you help me with?\nSuggest a short three-item plan for this evening.\nMake that plan shorter.\n/exit\n')
        run(['ollama','stop','gemma4:e2b'])
        run(['ollama','ps'])
        run([sys.executable,'wiki.py','search','localhost','--limit','2'])
        run([sys.executable,'check_vault.py'])
        result['disconnected_at_end'] = state('network-after-tests')
        stop_monitor.set();monitor.join(timeout=16)
        result['all_network_samples_disconnected'] = bool(samples) and all(x['disconnected'] for x in samples)
        result['network_sample_count'] = len(samples)
        result['status'] = 'completed' if result['disconnected_at_end'] and result['all_network_samples_disconnected'] and result['all_evaluation_checks_passed'] and result['reingestion_identical'] else 'needs-review'
        summary['network_status'] = ('Verified disconnected: Wi-Fi service disabled, no active network interfaces throughout sampling, external probes failed before and after.' if result['disconnected_at_end'] and result['all_network_samples_disconnected'] else 'Offline verification failed or incomplete; inspect network evidence.')
        summary['offline_evidence'] = folder.relative_to(ROOT).as_posix()
        save_json(evaluation,summary)
    except BaseException as exc:
        result['status']='failed';result['error']=str(exc)
        emit('ERROR: '+str(exc)+'\n')
    finally:
        stop_monitor.set()
        if monitor: monitor.join(timeout=16)
        save_json(folder/'network-samples.json',samples)
        restored_service = subprocess.run(['networksetup','-setnetworkserviceenabled','Wi-Fi','on'],capture_output=True,text=True,timeout=15)
        result['service_restore_exit']=restored_service.returncode
        result['service_after_restore']=capture(['networksetup','-getnetworkserviceenabled','Wi-Fi'])[0]
        restored = subprocess.run(['networksetup','-setairportpower',device,'on'],capture_output=True,text=True,timeout=15)
        result['restore_command_exit']=restored.returncode
        result['wifi_after_restore']=capture(['networksetup','-getairportpower',device])[0]
        if result['wifi_after_restore'].endswith(': On') and result['service_after_restore']=='Enabled': watchdog.terminate()
        result['elapsed_seconds']=round(time.monotonic()-started,3)
        save_json(folder/'result.json',result)
        emit('\nFINAL RESULT\n'+json.dumps(result,indent=2)+'\n')
        transcript.close();recording.close()
    print('OFFLINE_EVIDENCE='+str(folder.relative_to(ROOT)),flush=True)
    return 0 if result['status']=='completed' else 1


if __name__=='__main__':
    raise SystemExit(main())
