import os
import yaml

############### Default settings ###############

# OSC bridge settings
OSC_BRIDGE_IP = "127.0.0.1"
OSC_BRIDGE_PORT = 8088

# SuperCollider Settings
SC_IP = "127.0.0.1"
SC_PORT = 57120

############### YAML settings ###############

_yml_config_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'config.yml')

if os.path.exists(_yml_config_path):
    with open(_yml_config_path) as f:
        config = yaml.load(f, Loader=yaml.Loader)
        print('load config.yml')
        # OSC bridge settings
        OSC_BRIDGE_IP = config['osc_bridge_ip']
        OSC_BRIDGE_PORT = config['osc_bridge_port']

        # SuperCollider Settings
        SC_IP = config['sc_ip']
        SC_PORT = config['sc_port']
        print(SC_PORT)
