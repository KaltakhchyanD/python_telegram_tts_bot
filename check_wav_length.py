import os
import wave
import subprocess

#current_dir = os.getcwd()

#files_and_dirs_in_cwd = os.listdir(path=os.getcwd())


def get_duration(filename):
    with wave.open(filename) as wav_f:
        frames = wav_f.getnframes()
        rate = wav_f.getframerate()
        duration = frames / float(rate)
    return duration

#not_empty_wav_files = [i for i in sorted(files_and_dirs_in_cwd) if '.wav' in i and get_duration(i)>=0.5 and i !=  'new_test_voice.wav'    and i != 'text_from_speach.wav' and i != 'speech_test.wav']


def generate_small_files(source_wav):
    subprocess.call(['sox', source_wav, 'new_small_file.wav', 'silence', '0', '1', '0.1', '2%', ':', 'newfile', ':', 'restart'])
    #subprocess.call(['sox', 'text_from_speach.wav', 'new_small_file.wav', 'silence', '0', '1', '0.2', '2%', ':', 'newfile', ':', 'restart'])


def prepare_some_files(source_wav):
    files_and_dirs_in_cwd = os.listdir(path=os.getcwd())
    not_empty_wav_files = [i for i in sorted(files_and_dirs_in_cwd) if '.wav' in i and get_duration(i)>=0.5 and 'new_small_file' in i]
    print(f'NOT EMPTY FILES {not_empty_wav_files}')
    list_of_names = ['generated_audio_file.wav']

    with open(list_of_names[0], 'wb') as dst_wav_file:
        pass

    return (not_empty_wav_files, list_of_names)


def get_file_name(list_of_names):
    return list_of_names[-1]


def create_new_file_name(list_of_names):
    last_name = get_file_name(list_of_names)
    new_name = last_name.split('.')[0]+'_1'+'.wav'
    with open(new_name, 'w') as f:
        pass
    list_of_names.append(new_name)


def get_size(filename):
    return os.path.getsize(filename)/1024


def delete_old_files():
    files_and_dirs_in_cwd = os.listdir(path=os.getcwd())
    not_empty_wav_files = [i for i in sorted(files_and_dirs_in_cwd) if '.wav' in i]
    print(f'{len(not_empty_wav_files)} files to delete')    
    for filename in not_empty_wav_files:
        if 'new_small_file' in filename or 'generated_audio_file' in filename:
            print(f'Deleting file {filename}')
            os.remove(filename)


def do_the_thing(source_wav):
    print('Cleaning up')
    delete_old_files()
    print('Splitting to small files')
    generate_small_files(source_wav)

    not_empty_wav_files, list_of_names=prepare_some_files(source_wav)


    print(f'Start size {get_size(get_file_name(list_of_names))}')
    
    
    for file in not_empty_wav_files:
        kbytes = os.path.getsize(file)/1024
        print(f'File - {file}, size - {os.path.getsize(file)/1024} kb')
    
        current_file = get_file_name(list_of_names)
        current_size = get_size(current_file)
    
        if current_size + kbytes< 1024:
            pass
        else:
            print('     ------- LONG FILE')
    
            create_new_file_name(list_of_names)
            
            current_file = get_file_name(list_of_names)
            current_size = get_size(current_file)

        with open(current_file, 'rb') as src_file_wav:
            src_data = src_file_wav.read()
        with open(file, 'rb') as file_wav:
            file_data = file_wav.read()
        with wave.open(current_file, 'wb') as dst_wav_file:
            dst_wav_file.setparams((1, 2, 48000, 0, 'NONE', 'NONE' ))
            dst_wav_file.writeframes(src_data+file_data)
        print(f'New size {get_size(current_file)}')

    print(list_of_names)
    return list_of_names


if __name__ == '__main__':
    do_the_thing(source_wav = 'text_from_speach.wav')
