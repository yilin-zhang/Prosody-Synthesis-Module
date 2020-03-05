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
        'noiseness': (0, 1)
    }

    OUPUT_PARAMS = ('vowel1_f1', 'vowel1_f2', 'vowel2_f1', 'vowel2_f2', 'tune',
                    'vibrato', 'brightness', 'noiseness')

    def __init__(self):
        self._param_values = dict.fromkeys(ParamMapper.PARAM_RANGES, 0.)

    def update_param(self, param, value):
        ''' Update the parameter, and return a dict of the updated outputs
        Args:
        - param: the parameter
        - value: the value of the parameter
        Return:
        - a dict of updated output
        '''
        if not (value >= ParamMapper.PARAM_RANGES[param][0]
                and value <= ParamMapper.PARAM_RANGES[param][1]):
            return
        self._param_values[param] = value
        # you should handle what outputs should be updated here
        if param in ('valence', 'power'):
            return self._map_formants()
        else:
            return {param: self._param_values[param]}

    def _map_formants(self):
        '''Get the formant frequencies based on the current param_values'''
        formant_control_params = {
            'a': {
                'f1': 675,  # in Hz
                'f2': 1550,
                'f1_range': 75,  # in Hz
                'f2_range': 150,
                'f1_valence_ratio': 0.3,
                'f1_power_ratio': 0.7,
                'f2_valence_ratio': 0.9,
                'f2_power_ratio': 0.1,
            },
            'i': {
                'f1': 350,
                'f2': 2120,
                'f1_range': 120,
                'f2_range': 150,
                'f1_valence_ratio': -0.3,
                'f1_power_ratio': 0.7,
                'f2_valence_ratio': 0.7,
                'f2_power_ratio': 0.3,
            },
            'u': {
                'f1': 390,
                'f2': 1290,
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
