import pickle as p
import CONFIG as c

import note

class MIDIRecorder:
    def __init__(self,metronome):
        self.RECORD = False
        self.my_loop = []  # current recording loop
        self.metronome = metronome
        self.active_loops = []  # IDs of active subloops
        self.current_loop_length = 0
        self.current_loop_index = 0
        self.current_loop_id = -1
        self.my_tracks = {}
        self.tracks_path = c.PROGRAM_PATH + "my_tracks.pkl"
        try:
            self.my_tracks, _ = p.load(open(self.tracks_path,'rb'))
        except:
            print("Could not load saved tracks, or no saved tracks found.")


    """Switch ON/OFF MIDI Loop Recording and Increment Subloop ID"""
    def switch_record_button(self):
        if self.RECORD:
            print("LOOP RECORD OFF")
            self.RECORD = False
        else:
            print(f"LOOP RECORD ON / loop id: {self.current_loop_id}")
            self.current_loop_id += 1
            self.active_loops.append(self.current_loop_id)
            print(f"LOOP RECORD ON / loop id: {self.current_loop_id}")
            print(f"active loops: {self.active_loops}")
            self.RECORD = True

    """Activate or deactivate specific subloops in a track"""
    def activate_loop_id(self,id):  # activate or deactivate loop from midi controller
        if id in self.active_loops and id <= self.current_loop_id:
            self.active_loops.remove(id)
            print(f"adding loop id: {id}")
            print(f"active loops: {self.active_loops}")
        elif id not in self.active_loops and id <= self.current_loop_id:
            self.active_loops.append(id)
            print(f"removing loop id: {id}")
            print(f"active loops: {self.active_loops}")

    """Clear all the data in the current track"""
    def clear_all_loops(self):
        self.my_loop = []
        self.current_loop_length = 0
        self.current_loop_index = 0
        self.current_loop_id = -1
        self.active_loops = []

    """Add midi data point and loop ID to the current loop"""
    def add_entry(self,midi,port,when_added):
        self.my_loop.append(note.Note(self.metronome.get_position(timestamp=when_added),
                                      midi,
                                      self.metronome.controller.current_bank,
                                      port,
                                      when_added,
                                      self.current_loop_id,
                                      self.metronome.controller.current_page))
        self.current_loop_length = len(self.my_loop)
        self.my_loop.sort(key=lambda x: x.bar_position)  # re-sort the list every time a new item added

    """Save current track to tracklist and save to pickle file."""
    def save_track(self,id):
        self.my_tracks[id] = self.my_loop
        p.dump((self.my_tracks,self.current_loop_id), open(self.tracks_path,'wb'))
        print(f"TRACK SAVED TO SLOT: {id}")

    """Load a track from tracklist pickle file"""
    def load_track(self,id):
        try:
            self.my_tracks, self.current_loop_id = p.load(open(self.tracks_path,'rb'))
            self.my_loop = self.my_tracks[id]
            self.active_loops = [] #list(range(0, self.current_loop_id))
            self.current_loop_length = len(self.my_loop)
            print(f"TRACK {id} LOADED")
        except KeyError:
            print("TRACK NOT FOUND")
            pass
