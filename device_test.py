# device_test.py
# name=Test Controller

import transport
import ui
import midi
import channels
import playlist
import patterns
import arrangement
import general
import device
import time
import sys

# Global variables
receiving_mode = False
note_count = 0
values_received = 0
midi_data = []
midi_notes_array = []


def OnInit():
    """Called when the script is loaded by FL Studio"""
    print("Complex MIDI Receiver Initialized. Ready for data.")
    device.setHintMsg("Ready for data transfer.")
    return

def OnDeInit():
    """Called when the script is unloaded by FL Studio"""
    print("Complex MIDI Receiver Deinitialized.")
    return

def OnMidiMsg(event, timestamp=0):
    """Called when a processed MIDI message is received"""
    
    global receiving_mode, note_count, values_received, midi_data, midi_notes_array
    
    # Initialize globals if they don't exist
    if 'receiving_mode' not in globals():
        receiving_mode = False
    if 'note_count' not in globals():
        note_count = 0
    if 'values_received' not in globals():
        values_received = 0
    if 'midi_data' not in globals():
        midi_data = []
    if 'midi_notes_array' not in globals():
        midi_notes_array = []
    
    # Only process Note On messages with velocity > 0
    if event.status >= midi.MIDI_NOTEON and event.status < midi.MIDI_NOTEON + 16 and event.data2 > 0:
        note_value = event.data1
        
        # Toggle receiving mode with note 0
        if note_value == 0 and not receiving_mode:
            receiving_mode = True
            print("Started receiving MIDI notes")
            device.setHintMsg("Receiving data...")
            midi_data = []
            note_count = 0
            values_received = 0
            midi_notes_array = []
            event.handled = True
            return
        
        if not receiving_mode:
            return
        
        # Second message is the note count
        if note_count == 0 and values_received == 0:
            note_count = note_value
            print(f"Expecting {note_count} notes")
            values_received += 1 # Mark that we have received the count
            event.handled = True
            return
        
        # End of transmission signal
        if note_value == 127:
            print(f"Received termination signal. Processing {len(midi_notes_array)} notes.")
            receiving_mode = False
            if midi_notes_array:
                record_notes_batch(midi_notes_array)
            event.handled = True
            return

        # All subsequent messages are MIDI values
        midi_data.append(note_value)
        
        # Process completed notes (every 6 values)
        if len(midi_data) % 6 == 0:
            i = len(midi_data) - 6
            note = midi_data[i]
            velocity = midi_data[i+1]
            length_whole = midi_data[i+2]
            length_decimal = midi_data[i+3]
            position_whole = midi_data[i+4]
            position_decimal = midi_data[i+5]
            
            length = length_whole + (length_decimal / 10.0)
            position = position_whole + (position_decimal / 10.0)
            
            midi_notes_array.append((note, velocity, length, position))
            print(f"Received note {len(midi_notes_array)}/{note_count}: note={note}, pos={position}")

            if len(midi_notes_array) >= note_count:
                print(f"Received all {note_count} notes.")
                receiving_mode = False
                record_notes_batch(midi_notes_array)
                event.handled = True
                return
        
        event.handled = True

def record_notes_batch(notes_array):
    """
    Records a batch of notes to FL Studio, handling simultaneous notes properly
    
    Args:
        notes_array: List of tuples, each containing (note, velocity, length_beats, position_beats)
    """
    # Sort notes by their starting position
    sorted_notes = sorted(notes_array, key=lambda x: x[3])
    
    # Group notes by their starting positions
    position_groups = {}
    for note in sorted_notes:
        position = note[3]  # position_beats is the 4th element (index 3)
        if position not in position_groups:
            position_groups[position] = []
        position_groups[position].append(note)
    
    # Process each position group
    positions = sorted(position_groups.keys())
    for position in positions:
        notes_at_position = position_groups[position]
        
        # Find the longest note in this group to determine recording length
        max_length = max(note[2] for note in notes_at_position)
        
        # Make sure transport is stopped first
        if transport.isPlaying():
            transport.stop()
        
        # Get the current channel
        channel = channels.selectedChannel()
        
        # Get the project's PPQ (pulses per quarter note)
        ppq = general.getRecPPQ()
        
        # Calculate ticks based on beats
        position_ticks = int(position * ppq)
        
        # Set playback position
        transport.setSongPos(position_ticks, 2)  # 2 = SONGLENGTH_ABSTICKS
        
        # Toggle recording mode if needed
        if not transport.isRecording():
            transport.record()
        
        print(f"Recording {len(notes_at_position)} simultaneous notes at position {position}")
        
        # Start playback to begin recording
        transport.start()
        
        # Record all notes at this position simultaneously
        for note, velocity, length, _ in notes_at_position:
            channels.midiNoteOn(channel, note, int(velocity))
        
        # Get the current tempo
        try:
            import mixer
            tempo = mixer.getCurrentTempo()
            tempo = tempo/1000
        except (ImportError, AttributeError):
            tempo = 120  # Default fallback
            
        print(f"Using tempo: {tempo} BPM")
        
        # Calculate the time to wait in seconds based on the longest note
        seconds_to_wait = (max_length * 60) / tempo
        
        print(f"Waiting for {seconds_to_wait:.2f} seconds...")
        
        # Wait the calculated time
        time.sleep(seconds_to_wait)
        
        # Send note-off events for all notes
        for note, _, _, _ in notes_at_position:
            channels.midiNoteOn(channel, note, 0)
        
        # Stop playback
        transport.stop()
        
        # Exit recording mode if it was active
        if transport.isRecording():
            transport.record()
        
        # Small pause between recordings to avoid potential issues
        time.sleep(0.2)
    
    print("All notes recorded successfully")
    
    # Return to beginning
    transport.setSongPos(0, 2)
