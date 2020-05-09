import random
import math
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
                **self._map_detune(),
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
        hf_range = (-1.5, 1.5)  # in power db
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

    def _map_detune(self):
        detune_range = (0, -0.5)
        valence = self._param_values['valence']
        power = self._param_values['power']

        # calculate the angle
        angle = 0
        if valence != 0:
            angle = math.degrees(math.atan(power/valence))
        else:
            if power > 0:
                angle = 90
            elif power < 0:
                angle = -90
        if valence < 0:  # if it's the left half
            if angle > 0:
                angle -= 180
            else:
                angle += 180
        if angle < 0:  # make sure angle is in [0, 360)
            angle += 360

        angle_diff = abs(angle - 135)  # the distance to angry
        ratio = 1
        if angle_diff <= 45:
            # angle_diff = 360 - angle_diff
            ratio = angle_diff / 45
        detune = detune_range[0] * ratio + detune_range[1] * (1 - ratio)
        print('detune:', detune)
        return {'detune': detune}


    def _map_formants(self):
        '''Get the formant frequencies based on the current param_values'''
        formant_control_params = {
            'a': {
                'f1': 660,  # in Hz
                'f2': 1700,
                'f1_range': 75,  # in Hz
                'f2_range': 150,
                'f1_valence_ratio': 0.3,
                'f1_power_ratio': 0.7,
                'f2_valence_ratio': 0.9,
                'f2_power_ratio': 0.1,
            },
            'i': {
                'f1': 270,
                'f2': 2300,
                'f1_range': 120,
                'f2_range': 150,
                'f1_valence_ratio': -0.3,
                'f1_power_ratio': 0.7,
                'f2_valence_ratio': 0.7,
                'f2_power_ratio': 0.3,
            },
            'u': {
                'f1': 300,
                'f2': 870,
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

        def select_vowels(valence, power):
            quadrant_proba = (
                {'a': 0.1, 'i': 0.8, 'u': 0.1},  # quadrant 1, happy
                {'a': 0.8, 'i': 0.1, 'u': 0.1},  # quadrant 2, angry
                {'a': 0.1, 'i': 0.1, 'u': 0.8},  # quadrant 3, sad
                {'a': 0.4, 'i': 0.4, 'u': 0.2},  # quadrant 4, relief
            )

            def get_select_proba(idx_1, idx_2, ratio):
                select_proba =  {
                    'a': quadrant_proba[idx_1]['a'] * (1 - ratio) + quadrant_proba[idx_2]['a'] * ratio,
                    'i': quadrant_proba[idx_1]['i'] * (1 - ratio) + quadrant_proba[idx_2]['i'] * ratio,
                    'u': quadrant_proba[idx_1]['u'] * (1 - ratio) + quadrant_proba[idx_2]['u'] * ratio,
                }
                # normalize
                norm_select_proba = select_proba
                norm_select_proba['a']  = select_proba['a'] / sum(select_proba.values())
                norm_select_proba['i']  = select_proba['i'] / sum(select_proba.values())
                norm_select_proba['u']  = select_proba['u'] / sum(select_proba.values())
                return norm_select_proba

            def get_vowel(select_proba):
                rand_num = random.random()
                if rand_num <= select_proba['a']:
                    return 'a'
                if rand_num <= select_proba['a'] + select_proba['i']:
                    return 'i'
                return 'u'

            # calculate the angle
            angle = 0
            if valence != 0:
                angle = math.degrees(math.atan(power/valence))
            else:
                if power > 0:
                    angle = 90
                elif power < 0:
                    angle = -90

            if valence < 0:  # if it's the left half
                if angle > 0:
                    angle -= 180
                else:
                    angle += 180

            if angle >= -45 and angle < 45:      # 4 and 1
                ratio = (angle - (-45)) / 90
                select_proba = get_select_proba(3, 0, ratio)
            elif angle >= 45 and angle < 135:    # 1 and 2
                ratio = (angle - 45) / 90
                select_proba = get_select_proba(0, 1, ratio)
            elif angle >= 135 or angle < -135:   # 2 and 3
                if angle < -135:
                    angle += 360
                ratio = (angle - 135) / 90
                select_proba = get_select_proba(1, 2, ratio)
            elif angle >= -135 and angle < -45:  # 3 and 4
                ratio = (angle - (-135)) / 90
                select_proba = get_select_proba(2, 3, ratio)

            # select vowels based on probability
            vowel1 = get_vowel(select_proba)
            vowel2 = get_vowel(select_proba)

            return vowel1, vowel2

        valence = self._param_values['valence']
        power = self._param_values['power']

        vowel1, vowel2 = select_vowels(valence, power)
        print('vowels:', vowel1 + vowel2)

        vowel1_f1, vowel1_f2 = map_vowel(vowel1, valence, power)
        vowel2_f1, vowel2_f2 = map_vowel(vowel2, valence, power)

        return {
            'vowel1_f1': vowel1_f1,
            'vowel1_f2': vowel1_f2,
            'vowel2_f1': vowel2_f1,
            'vowel2_f2': vowel2_f2
        }
