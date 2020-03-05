'''
The class CCMapper handles the cc channel mappings.

Control Parameters:
- CC0 Valence
- CC1 Power
- CC2 Tune (microtone control, +- 100 cents, value 64 -> 0 cent)
- CC3 Vibrato
- CC4 Brightness
- CC5 Noisiness
'''

import random
from typing import List, Tuple
import mido
from mido.messages.messages import Message


class CCMapper():

    INPUT_CC_NUMBERS = {
        'valence': 0,
        'power': 1,
        'tune': 2,
        'vibrato': 3,
        'brightness': 4,
        'noiseness': 5
    }

    OUTPUT_CC_NUMBERS = {
        'vowel1': 0,
        'vowel1_f1': 1,
        'vowel1_f2': 2,
        'vowel2': 3,
        'vowel2_f1': 4,
        'vowel2_f2': 5,
        'tune': 6,
        'vibrato': 7,
        'brightness': 8,
        'noiseness': 9
    }

    def __init__(self):
        # This is just a short cut. The values in the following dicts are
        # parameter values, rather than CC numbers.
        self._control_values = dict.fromkeys(CCMapper.INPUT_CC_NUMBERS, 0)

    def map(self, msg: Message) -> List[Message]:
        ''' Maps a CC message to one or multiple messages to be sent to the synth
        '''
        # TODO: for now only formants need to be mapped, other values can
        # be directly coped to the corresponding CC numbers.
        new_msgs = []
        for param, number in CCMapper.INPUT_CC_NUMBERS.items():
            if number == msg.control:
                # update interval control values
                self._control_values[param] = msg.value
                # handle 2d emotion
                if param == 'valence' or param == 'power':
                    new_vals = self._map_2d_emotion(
                        self._control_values['valence'],
                        self._control_values['power'])
                    keys = [
                        'vowel1', 'vowel1_f1', 'vowel1_f2', 'vowel2',
                        'vowel2_f1', 'vowel2_f2'
                    ]
                    for idx, f in enumerate(new_vals):
                        new_msgs.append(
                            msg.copy(
                                control=CCMapper.OUTPUT_CC_NUMBERS[keys[idx]],
                                value=f))
                # handle other paramters
                else:
                    new_msgs.append(
                        msg.copy(control=CCMapper.OUTPUT_CC_NUMBERS[param],
                                 value=self._control_values[param]))
                break

        return new_msgs

    def _map_2d_emotion(self, valence: int,
                        power: int) -> Tuple[int, int, int, int, int, int]:
        # TODO: the two vowels are randomly chosen, maybe improve this in the
        # future
        # TODO: The central formants can be useful in the future
        formant_control_params = {
            'a': {
                # 'f1': 675,  # in Hz
                # 'f2': 1550,
                # 'f1_range': 75,  # in Hz
                # 'f2_range': 150,
                'f1_valence_ratio': 0.3,
                'f1_power_ratio': 0.7,
                'f2_valence_ratio': 0.9,
                'f2_power_ratio': 0.1,
            },
            'i': {
                # 'f1': 350,
                # 'f2': 2120,
                # 'f1_range': 120,
                # 'f2_range': 150,
                'f1_valence_ratio': -0.3,
                'f1_power_ratio': 0.7,
                'f2_valence_ratio': 0.7,
                'f2_power_ratio': 0.3,
            },
            'u': {
                # 'f1': 390,
                # 'f2': 1290,
                # 'f1_range': 90,
                # 'f2_range': 70,
                'f1_valence_ratio': 0.4,
                'f1_power_ratio': 0.6,
                'f2_valence_ratio': 0.3,
                'f2_power_ratio': 0.7,
            }
        }

        def map_vowel(vowel: str, valence: int, power: int) -> Tuple[int, int]:
            valence_scale = (valence / 127. - 0.5) * 2
            power_scale = (power / 127. - 0.5) * 2
            vowel_params = formant_control_params[vowel]

            output_f1 = round(
                (vowel_params['f1_valence_ratio'] * valence_scale +
                 vowel_params['f1_power_ratio'] * power_scale + 1) / 2 * 127)
            output_f2 = round(
                (vowel_params['f2_valence_ratio'] * valence_scale +
                 vowel_params['f2_power_ratio'] * power_scale + 1) / 2 * 127)

            return output_f1, output_f2

        def vowel_str_to_int(vowel: str) -> int:
            if vowel == 'a':
                return 0
            if vowel == 'i':
                return 1
            if vowel == 'u':
                return 2
            return -1

        vowels = formant_control_params.keys()
        vowel1, vowel2 = random.sample(vowels, 2)

        vowel1_f1, vowel1_f2 = map_vowel(vowel1, valence, power)
        vowel2_f1, vowel2_f2 = map_vowel(vowel2, valence, power)

        return vowel_str_to_int(
            vowel1), vowel1_f1, vowel1_f2, vowel_str_to_int(
                vowel2), vowel2_f1, vowel2_f2
