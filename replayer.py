import os
import time
import logging
from dotenv import load_dotenv
from scapy.all import sniff, ARP

load_dotenv()

CHANNEL_ID = int(os.environ['CHANNEL_ID'])
double_sniff = False
last_event_id = None

from pynput.keyboard import Controller as KeyboardController, Key, KeyCode
from pynput.mouse import Controller as MouseController, Button

keyboard = KeyboardController()
mouse = MouseController()
screen_width = 0
screen_height = 0
is_win = (os.name == 'nt')

from screeninfo import get_monitors
for m in get_monitors():
  if m.is_primary:
    screen_width = m.width
    screen_height = m.height
    break


def two_bytes_to_signed_int(high_byte, low_byte):
    # Combine high and low bytes to form a 16-bit integer
    combined = (high_byte << 8) | low_byte
    # Convert to signed integer
    signed_int = combined if combined < 32768 else combined - 65536
    return signed_int

def byte_to_signed_int(byte):
    if byte > 127:
        return byte - 256
    else:
        return byte

def scale_coordinate(value, max_value):
  # Scale from the range -32768 to 32767 to 0 to max_value
  return (value + 32768) * max_value / 65535

def get_pynput_key(key_code):
    key_mapping = {
        "KeyA": KeyCode.from_char('a'),
        "KeyB": KeyCode.from_char('b'),
        "KeyC": KeyCode.from_char('c'),
        "KeyD": KeyCode.from_char('d'),
        "KeyE": KeyCode.from_char('e'),
        "KeyF": KeyCode.from_char('f'),
        "KeyG": KeyCode.from_char('g'),
        "KeyH": KeyCode.from_char('h'),
        "KeyI": KeyCode.from_char('i'),
        "KeyJ": KeyCode.from_char('j'),
        "KeyK": KeyCode.from_char('k'),
        "KeyL": KeyCode.from_char('l'),
        "KeyM": KeyCode.from_char('m'),
        "KeyN": KeyCode.from_char('n'),
        "KeyO": KeyCode.from_char('o'),
        "KeyP": KeyCode.from_char('p'),
        "KeyQ": KeyCode.from_char('q'),
        "KeyR": KeyCode.from_char('r'),
        "KeyS": KeyCode.from_char('s'),
        "KeyT": KeyCode.from_char('t'),
        "KeyU": KeyCode.from_char('u'),
        "KeyV": KeyCode.from_char('v'),
        "KeyW": KeyCode.from_char('w'),
        "KeyX": KeyCode.from_char('x'),
        "KeyY": KeyCode.from_char('y'),
        "KeyZ": KeyCode.from_char('z'),
        "Digit1": KeyCode.from_char('1') if is_win else KeyCode(vk=18),
        "Digit2": KeyCode.from_char('2') if is_win else KeyCode(vk=19),
        "Digit3": KeyCode.from_char('3') if is_win else KeyCode(vk=20),
        "Digit4": KeyCode.from_char('4') if is_win else KeyCode(vk=21),
        "Digit5": KeyCode.from_char('5') if is_win else KeyCode(vk=23),
        "Digit6": KeyCode.from_char('6') if is_win else KeyCode(vk=22),
        "Digit7": KeyCode.from_char('7') if is_win else KeyCode(vk=26),
        "Digit8": KeyCode.from_char('8') if is_win else KeyCode(vk=28),
        "Digit9": KeyCode.from_char('9') if is_win else KeyCode(vk=25),
        "Digit0": KeyCode.from_char('0') if is_win else KeyCode(vk=29),
        "Enter": Key.enter,
        "Escape": Key.esc,
        "Backspace": Key.backspace,
        "Tab": Key.tab,
        "Space": Key.space,
        "Minus": KeyCode.from_char('-') if is_win else KeyCode(vk=27),
        "Equal": KeyCode.from_char('=') if is_win else KeyCode(vk=24),
        "BracketLeft": KeyCode.from_char('[') if is_win else KeyCode(vk=33),
        "BracketRight": KeyCode.from_char(']') if is_win else KeyCode(vk=20),
        "Backslash": KeyCode.from_char('\\') if is_win else KeyCode(vk=42),
        "Semicolon": KeyCode.from_char(';') if is_win else KeyCode(vk=41),
        "Quote": KeyCode.from_char('\'') if is_win else KeyCode(vk=39),
        "Backquote": KeyCode.from_char('`') if is_win else KeyCode(vk=50),
        "Comma": KeyCode.from_char(',') if is_win else KeyCode(vk=43),
        "Period": KeyCode.from_char('.') if is_win else KeyCode(vk=47),
        "Slash": KeyCode.from_char('/') if is_win else KeyCode(vk=44),
        "CapsLock": Key.caps_lock if is_win else KeyCode(vk=57),
        "F1": Key.f1,
        "F2": Key.f2,
        "F3": Key.f3,
        "F4": Key.f4,
        "F5": Key.f5,
        "F6": Key.f6,
        "F7": Key.f7,
        "F8": Key.f8,
        "F9": Key.f9,
        "F10": Key.f10,
        "F11": Key.f11,
        "F12": Key.f12,
        "PrintScreen": Key.print_screen if is_win else None,
        "ScrollLock": Key.scroll_lock if is_win else None,
        "Pause": Key.pause if is_win else None,
        "Insert": Key.insert if is_win else None,
        "Home": Key.home,
        "PageUp": Key.page_up,
        "Delete": Key.delete,
        "End": Key.end,
        "PageDown": Key.page_down,
        "ArrowRight": Key.right,
        "ArrowLeft": Key.left,
        "ArrowDown": Key.down,
        "ArrowUp": Key.up,
        # "NumLock": Key.num_lock,
        "NumpadDivide": KeyCode.from_char('/'),
        "NumpadMultiply": KeyCode.from_char('*'),
        "NumpadSubtract": KeyCode.from_char('-'),
        "NumpadAdd": KeyCode.from_char('+'),
        "NumpadEnter": Key.enter,
        "Numpad1": KeyCode.from_char('1'),
        "Numpad2": KeyCode.from_char('2'),
        "Numpad3": KeyCode.from_char('3'),
        "Numpad4": KeyCode.from_char('4'),
        "Numpad5": KeyCode.from_char('5'),
        "Numpad6": KeyCode.from_char('6'),
        "Numpad7": KeyCode.from_char('7'),
        "Numpad8": KeyCode.from_char('8'),
        "Numpad9": KeyCode.from_char('9'),
        "Numpad0": KeyCode.from_char('0'),
        "NumpadDecimal": KeyCode.from_char('.'),
        "ShiftLeft": Key.shift,
        "ShiftRight": Key.shift_r,
        "ControlLeft": Key.ctrl,
        "ControlRight": Key.ctrl_r,
        "AltLeft": Key.alt,
        "AltRight": Key.alt_r,
        "MetaLeft": Key.cmd,
        "MetaRight": Key.cmd_r,
        "ContextMenu": Key.menu,
        # Add more if needed, depending on your specific requirements
    }

    return key_mapping.get(key_code, None)

def decode_hid_event(data):
    event = {}
    event_type_code = data[0]

    if event_type_code == 1:
        # Key event
        key = data[2:].decode('utf-8')
        if key is None:
            return
        event['type'] = 'key'
        event['state'] = data[1] == 1
        event['key'] = key

    elif event_type_code == 2:
        # Mouse button event
        event['type'] = 'mouse_button'
        event['state'] = data[1] == 1
        event['button'] = data[2:].decode('utf-8')

    elif event_type_code == 3:
        # Mouse move event
        event['type'] = 'mouse_move'
        event['to'] = {
            'x': two_bytes_to_signed_int(data[1], data[2]),
            'y': two_bytes_to_signed_int(data[3], data[4]),
        }

    elif event_type_code == 5:
        # Mouse wheel event
        event['type'] = 'mouse_wheel'
        event['squash'] = data[1] == 1
        event['delta'] = {
            'x': byte_to_signed_int(data[2]),
            'y': byte_to_signed_int(data[3]),
        }

    # else:
    #     raise ValueError(f"Unknown event type code: {event_type_code}")

    return event

click_count = 0
def replay_event(event):
  global click_count
  if event['type'] == 'key':
    key = get_pynput_key(event['key'])
    if key is None:
      return
    if event['state']:
      keyboard.press(key)
    else:
      keyboard.release(key)
    click_count = 0
  
  elif event['type'] == 'mouse_button':
    button = None
    if event['button'] == 'left':
      button = Button.left
    elif event['button'] == 'right':
      button = Button.right
    elif event['button'] == 'middle':
      button = Button.middle
    else:
      return
        
    if event['state']:
      if not is_win and button == Button.left:
        click_count += 1
        if click_count == 2:
          click_count = 0
          mouse.click(button)
          return
      else:
        click_count = 0
      mouse.press(button)
    else:
      mouse.release(button)

  elif event['type'] == 'mouse_move':
    pixel_x = int(scale_coordinate(event['to']['x'], screen_width))
    pixel_y = int(scale_coordinate(event['to']['y'], screen_height))
    mouse.position = (pixel_x, pixel_y)
    click_count = 0

  # elif event['type'] == 'mouse_relative':
  #     for delta in event['delta']:
  #         mouse.move(delta['x'], delta['y'])

  elif event['type'] == 'mouse_wheel':
    # The actual library method is `scroll`; this might differ slightly
    mouse.scroll(event['delta']['x'], event['delta']['y'])
    click_count = 0

def process_message(message):
    # print(message)
    hid_event = decode_hid_event(message)
    replay_event(hid_event)

def process_packet(packet):
    global double_sniff, last_event_id
    if ARP in packet and packet[ARP].op == 1:  # ARP request
        arppayload = bytes(packet[ARP])[28:]
        if len(arppayload) < 2 or arppayload[0] != CHANNEL_ID:
            return
        event_id = arppayload[1]
        if last_event_id == event_id:
            return
        last_event_id = event_id
        extra_data = arppayload[2:]
        if len(extra_data) > 0:
            try:
                process_message(extra_data)
            except:
                pass

if __name__ == "__main__":
    print("Starting...")
    while True:
        try:
            sniff(filter="arp", prn=process_packet, store=0)
        except Exception as e:
            logging.error(e)
        time.sleep(5)