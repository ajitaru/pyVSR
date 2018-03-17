from os import path
from natsort import natsorted

_current_path = path.abspath(path.dirname(__file__))


def request_files(dataset_dir,
                  protocol='speaker_independent',
                  speaker_id=None,
                  view_id='1',
                  utterance_types='dst',
                  content='video'):

    if protocol == 'single_speaker':
        train, test = _preload_files_single_volunteer(dataset_dir, speaker_id, view_id, utterance_types)
    elif protocol == 'speaker_independent':
        train, test = _preload_files_speaker_independent(dataset_dir, view_id, utterance_types)
        if content == 'audio':
            import re
            train = [re.sub('_v\d_', '_', file) for file in train]
            train = [re.sub('.mp4', '.wav', file) for file in train]
            test = [re.sub('_v\d_', '_', file) for file in test]
            test = [re.sub('.mp4', '.wav', file) for file in test]
    else:
        raise Exception('undefined dataset split protocol')

    return natsorted(train), natsorted(test)


def _preload_files_single_volunteer(dataset_dir, speaker_id, view_id, utterance_types):

    all_videos = path.join(_current_path, 'splits/allVideos.txt')

    u_list = _gen_utterance_list(utterance_types)

    with open(all_videos, 'r') as f:
        contents = f.read().splitlines()

    video_list = [path.join(dataset_dir, line)
                  for line in contents
                  if 's' + str(speaker_id) + '_' in line
                  if 'v' + str(view_id) in line
                  if any(u in line for u in u_list)]

    from sklearn.model_selection import train_test_split
    train, test = train_test_split(video_list, test_size=0.30, random_state=0)

    return train, test


def _preload_files_speaker_independent(dataset_dir, view_id, utterance_types):

    train_script = path.join(_current_path, 'splits/speaker_independent/train2.scp')
    test_script = path.join(_current_path, 'splits/speaker_independent/test2.scp')

    u_list = _gen_utterance_list(utterance_types)

    with open(train_script, 'r') as ftr:
        contents = ftr.read().splitlines()

        train_files = [path.join(dataset_dir, line)
                       for line in contents
                       if 'v' + str(view_id) in line
                       if any(u in line for u in u_list)]

    with open(test_script, 'r') as fte:
        contents = fte.read().splitlines()

        test_files = [path.join(dataset_dir, line)
                      for line in contents
                      if 'v' + str(view_id) in line
                      if any(u in line for u in u_list)]

    return train_files, test_files


def _gen_utterance_list(utype):
    u_list = []
    if 'd' in utype:
        u_list.extend(list(range(1, 31)))
    if 's' in utype:
        u_list.extend(list(range(31, 61)))
    if 't' in utype:
        u_list.extend(list(range(61, 71)))
    u_list = ['u' + str(u) + '.' for u in u_list]

    return u_list


def read_sentence_labels(file, unit='character'):

    with open(path.join(_current_path, 'configs', 'labels'), 'r') as f:
        contents = f.read().splitlines()

    labels_dict = dict([(line.split(' ', 1)) for line in contents])

    sentence = labels_dict[file]

    parsed_sentence = sentence.replace(' ', '_')
    parsed_sentence = parsed_sentence.lower()

    return str(parsed_sentence)


def read_all_sentences_labels():
    with open(path.join(_current_path, 'configs', 'labels'), 'r') as f:
        contents = f.read().splitlines()

    labels_dict = dict([(line.split(' ', 1)) for line in contents])

    parsed_dict = {}
    for (k,v) in labels_dict.items():
        parsed_sentence = v.replace(' ', '_')
        parsed_sentence = parsed_sentence.lower()
        parsed_dict[k] = list(parsed_sentence)

    return parsed_dict


