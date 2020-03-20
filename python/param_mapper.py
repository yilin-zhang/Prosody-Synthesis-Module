import random
from typing import List, Tuple, Dict
from mido.messages.messages import Message


class ParamMapper():
    PARAM_RANGES = {
        'valence': (-1, 1),
        'power': (-1, 1),
        'tune': (-1, 1),
        'vibrato': (0, 1),
        'brightness': (0, 1),
        'noisiness': (0, 1)
    }

    def __init__(self):
        self._param_values = dict.fromkeys(ParamMapper.PARAM_RANGES, 0.)

    def send_event(self, event, value=0):
        ''' Send an event and a value(optional), and return a dict of the
        updated outputs
        Args:
        - event: An event, including all the parameters and note_on
        - value: the value of the parameter
        Return:
        - a dict of updated output
        '''
        if event == 'note_on':  # map emotion-driven outputs
            return {
                **self._map_attack(),
                **self._map_lf_hf(),
                **self._map_formants()
            }
        if event in ('valence', 'power'):  # only update
            self._update(event, value)
            return {}
        if event in ('tune', 'vibrato', 'brightness',
                     'noisiness'):  # no mapping
            self._update(event, value)
            return {event: self._param_values[event]}

    def _update(self, param, value):
        if not (value >= ParamMapper.PARAM_RANGES[param][0]
                and value <= ParamMapper.PARAM_RANGES[param][1]):
            return
        self._param_values[param] = value

    def _map_attack(self):
        attack_range = (0.01, 0.5)
        scaled_power = -(self._param_values['power'] - 1) / 2
        attack = scaled_power * (attack_range[1] -
                                 attack_range[0]) + attack_range[0]
        print('attack:', attack)
        return {'attack': attack}

    def _map_lf_hf(self):
        hf_range = (-5, 5)  # in power db
        valence_ratio = -0.5
        power_ratio = 0.5
        valence = self._param_values['valence']
        power = self._param_values['power']

        hf_db = (hf_range[1] - hf_range[0]) * (
            valence_ratio * valence +
            power_ratio * power) / 2 + (hf_range[0] + hf_range[1]) / 2
        hf_ratio = 10**(hf_db / 20)
        lf_ratio = 1 / hf_ratio
        print('lf_ratio:', lf_ratio)
        print('hf_ratio:', hf_ratio)

        return {'lf_ratio': lf_ratio, 'hf_ratio': hf_ratio}

    def _map_formants(self):
        '''Get the formant frequencies based on the current param_values'''
        formant_control_params = {
            'a': {
                'f1': 850,  # in Hz
                'f2': 1610,
                'f1_range': 75,  # in Hz
                'f2_range': 150,
                'f1_valence_ratio': 0.3,
                'f1_power_ratio': 0.7,
                'f2_valence_ratio': 0.9,
                'f2_power_ratio': 0.1,
            },
            'i': {
                'f1': 240,
                'f2': 2400,
                'f1_range': 120,
                'f2_range': 150,
                'f1_valence_ratio': -0.3,
                'f1_power_ratio': 0.7,
                'f2_valence_ratio': 0.7,
                'f2_power_ratio': 0.3,
            },
            'u': {
                'f1': 250,
                'f2': 595,
                'f1_range': 90,
                'f2_range': 70,
                'f1_valence_ratio': 0.4,
                'f1_power_ratio': 0.6,
                'f2_valence_ratio': 0.3,
                'f2_power_ratio': 0.7,
            }
        }

        def map_vowel(vowel, valence, power):
            vowel_params = formant_control_params[vowel]
            f1 = (vowel_params['f1_valence_ratio'] * valence +
                  vowel_params['f1_power_ratio'] *
                  power) * vowel_params['f1_range'] + vowel_params['f1']
            f2 = (vowel_params['f2_valence_ratio'] * valence +
                  vowel_params['f2_power_ratio'] *
                  power) * vowel_params['f2_range'] + vowel_params['f2']
            return f1, f2

        # randomly picking vowels
        vowels = formant_control_params.keys()
        vowel1, vowel2 = random.sample(vowels, 2)
        print('vowels:', vowel1 + vowel2)
        vowel1_f1, vowel1_f2 = map_vowel(vowel1, self._param_values['valence'],
                                         self._param_values['power'])
        vowel2_f1, vowel2_f2 = map_vowel(vowel2, self._param_values['valence'],
                                         self._param_values['power'])

        return {
            'vowel1_f1': vowel1_f1,
            'vowel1_f2': vowel1_f2,
            'vowel2_f1': vowel2_f1,
            'vowel2_f2': vowel2_f2
        }
