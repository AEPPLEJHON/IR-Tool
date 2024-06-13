print("Status: Loading Kivy Modules")
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.core.audio import SoundLoader 
from kivy.utils import platform
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.uix.widget import Widget


from kivymd.app import MDApp
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDFillRoundFlatButton

import graph_subplot_widget

import wave
import numpy as np
import dsp
import os
import matplotlib.pyplot as plt
import csv

if platform == 'android':
  print("Status: Android Detected - Importing Android-Related Libraries")
  from audiostream import get_input
  from android.permissions import request_permissions, Permission
  from android.storage import primary_external_storage_path
  request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])
elif platform == 'win' or platform == 'macosx' or platform == 'linux':
  print(f"Status: \"{platform}\" Detected - Importing PC-Related Libraries")
  import pyaudio
else:
  print("Error: Platform Not Recognized!")
  

Builder.load_string('''
<IRTool>:
  orientation: 'vertical'
  padding:dp(2)
  MDBoxLayout: 
    id: display
    MDLabel:
      id: display_label
      text: '00:00'
      size_hint_y: None
      height: dp(100)
      halign: 'center'
      theme_text_color: 'Primary'
      font_size: '16sp'
      font_style:'Body1'

  Widget:
    size_hint_y:None
    height:dp(20)
  MDBoxLayout:
    size_hint_y: None
    orientation: 'horizontal'
    padding: dp(30)
    spacing: dp(20)
    MDTextField:
      valign: 'center'
      padding: dp(20)
      halign: 'center'
      height: dp(10)
      width: dp(20)
      mode: "line"
      pos_hint: {'center_x': 0.5, 'center_y': 0.48}
      size_hint_x: 0.6
      id: sweep_counter
      icon_right: "numeric"
      text: '1'
      multiline: False
      halign: 'center'
      size_hint_y: None
      height: dp(50)
      hint_text: "Number of Sweeps"
      helper_text: "Number of sine sweeps in measurement (positive int)"
    MDTextField:
      valign: 'center'
      padding: dp(20)
      halign: 'center'
      height: dp(10)
      width: dp(20)
      mode: "line"
      pos_hint: {'center_x': 0.5, 'center_y': 0.48}
      size_hint_x: 0.6
      id: tail_duration
      icon_right: "timer-plus-outline"
      text: '2'
      multiline: False
      halign: 'center'
      size_hint_y: None
      height: dp(50)
      hint_text: "Reverb Decay [s]"
      helper_text: "Measurement window after sweep (int)"
      
          
      
  #MDBoxLayout:
  #  size_hint_y: None
  #  padding: dp(10)
  #  height: dp(50)
   # orientation: 'horizontal'
  # MDLabel:
   #   valign: 'center'
   #   halign: 'center'
   #   text: 'Toggle Timer'
   #   theme_text_color: 'Primary'
   # MDSwitch:
   #   valign: 'center'
   #   width: dp(50)
   #   halign: 'center'
   #   id: duration_switch

  MDBoxLayout:
    size_hint_y: None
    height: dp(50)
    orientation: 'horizontal'
    spacing: dp(10)  # Optional: adds spacing between buttons
    padding: dp(10)  # Optional: adds padding inside the container

    MDFillRoundFlatIconButton:
      id: sine_sweep_param
      text: 'Sweep'
      font_size: '12sp'
      icon: 'sine-wave'
      size_hint_x: 0.33
      md_bg_color: 153/255, 0, 0, 1
      theme_text_color: 'Custom'
      text_color: 1, 1, 1, 1
      disabled: True
      on_release: root.sine_sweep_tab()

    MDFillRoundFlatIconButton:
      id: acoustic_param
      text: 'Metrics'
      icon: 'format-list-bulleted'
      font_size: '12sp'
      size_hint_x: 0.33
      md_bg_color: 153/255, 0, 0, 1
      theme_text_color: 'Custom'
      text_color: 1, 1, 1, 1
      on_release: root.acoustic_param_tab()

    MDFillRoundFlatIconButton:
      id: advanced_settings
      text: 'Adv. Settings'
      icon: 'cogs'
      font_size: '12sp'
      size_hint_x: 0.33
      md_bg_color: 153/255, 0, 0, 1
      theme_text_color: 'Custom'
      text_color: 1, 1, 1, 1
      on_release: root.advanced_settings_tab()
      
    MDFillRoundFlatIconButton:
      id: hide_button
      icon: 'triangle-small-down'
      text: ' Hide '
      font_size: '12sp'
      size_hint_x: 0.1
      md_bg_color: 153/255, 0, 0, 1
      theme_text_color: 'Custom'
      text_color: 1, 1, 1, 1
      on_release: root.hide_tabs()
      
  Widget:
    size_hint_y:None
    id: spacer1
    height:dp(20)
    
  MDBoxLayout:
    id: box1
    size_hint_y: None
    height: dp(40)
    orientation: 'horizontal'
    padding: dp(10)
    spacing: dp(10)
    
  Widget:
    size_hint_y:None
    id: spacer2
    height:dp(15)

  MDBoxLayout:
    id: box2
    size_hint_y: None
    height: dp(40)
    orientation: 'horizontal'
    padding: dp(10)
    spacing: dp(10)
    
  Widget:
    size_hint_y:None
    id: spacer3
    height:dp(15)
    
  MDBoxLayout:
    id: box3
    size_hint_y: None
    height: dp(40)
    orientation: 'horizontal'
    padding: dp(10)
    spacing: dp(10)
  
  Widget:
    size_hint_y:None
    id: spacer4
    height:dp(15)
    
  MDBoxLayout:
    id: box4
    size_hint_y: None
    height: dp(40)
    orientation: 'horizontal'
    padding: dp(10)
    spacing: dp(10)
    
  Widget:
    size_hint_y:None
    id: spacer5
    height:dp(15)
    
  MDBoxLayout:
    id: box5
    size_hint_y: None
    height: dp(40)
    orientation: 'horizontal'
    padding: dp(10)
    spacing: dp(10)

  MDBoxLayout:
    size_hint_y: None
    height: dp(50)
    orientation: 'horizontal'
    spacing: dp(10) 
    padding: dp(10)
    height: dp(70)
    
    MDFillRoundFlatIconButton:
      icon: 'timer-play'
      id: start_button
      text: 'Start Measurement'
      md_bg_color: 153/255, 0, 0, 1
      theme_text_color: 'Custom'
      text_color: 1, 1, 1, 1
      on_release: root.startMeasurementClock()
      md_stretch: True
      size_hint_x: 0.5
    MDFillRoundFlatIconButton:
      icon: "timer-remove"
      size_hint_x: 0.5
      id: stop_button
      text: 'Stop Measurement'
      md_bg_color: 153/255, 0, 0, 1
      theme_text_color: 'Custom'
      text_color: 1, 1, 1, 1
      on_release: root.stopButton()
      disabled: True
      md_stretch: True

  MDBoxLayout:
    halign: 'center'
    height: dp(70)
    size_hint_y: None
    orientation: 'horizontal'
    padding: dp(10)
    spacing: dp(20) 
    MDFillRoundFlatIconButton:
      icon: 'calculator-variant'
      id: generate_ir
      text: 'Generate IR'
      md_bg_color: 153/255, 0, 0, 1
      theme_text_color: 'Custom'
      text_color: 1, 1, 1, 1
      on_release: root.generateIRSignal()
      disabled: True
      size_hint_x: 0.7
      #pos_hint: {'center_x': 0.5, 'center_y': 0.51}
    MDFillRoundFlatIconButton:
      size: dp(20), dp(20)
      size_hint_x: None
      
      id: play_button
      theme_icon_color: "Custom"
      icon: "play"
      icon_color: "white"
      text: 'Play IR'
      md_bg_color: 153/255, 0, 0, 1
      on_release: root.playIR()
      disabled: True
      padding: dp(10)

    MDFillRoundFlatIconButton:
      size: dp(20), dp(20)
      size_hint_x: None
      
      id: stop_audio_button
      theme_icon_color: "Custom"
      icon: "stop"
      icon_color: "white"
      text: 'Stop IR'
      md_bg_color: 153/255, 0, 0, 1
      on_release: root.stopIR()
      disabled: True
      padding: dp(10)
  Widget:
    size_hint_y:None
    height:dp(15)

  MDBoxLayout:
    
    size_hint_y: None
    height: dp(50)
    spacing: dp(20) 
    padding: dp(10)
    orientation: 'horizontal'
    MDTextField:
      multiline: False
      id: save_file_name
      text: 'signal_file'
      multiline: False
      halign: 'center'
      icon_right: "file-document-edit"
      pos_hint: {'center_x': 0.5, 'center_y': 0.48}
      hint_text: "File Prefix"
      helper_text: "All files names will start with this Prefix"
    MDFillRoundFlatIconButton:
      id: save_button
      text: 'Save Files (WAV+CSV)'
      md_bg_color: 153/255, 0, 0, 1
      theme_text_color: 'Custom'
      text_color: 1, 1, 1, 1
      on_release: root.saveFileCaller()
      disabled: True
      icon: "content-save"
  Widget:
    size_hint_y:None
    height:dp(20)

''')

class DSPApp(MDApp):
  def build (self):
      self.theme_cls.primary_palette = "Red"
      self.theme_cls.primary_hue = "900"
      self.theme_cls.theme_style = "Light"
      Window.clearcolor = (1, 1, 1, 1) 
      
      return IRTool()
    
    
class IRTool(BoxLayout):
  def __init__(self, **kwargs):
      
    
      
    super(IRTool, self).__init__(**kwargs)
    
    self.start_button = self.ids['start_button']
    self.stop_button = self.ids['stop_button']
    self.display_label = self.ids['display_label']
    #self.switch = self.ids['duration_switch']
    self.tail_duration_text = self.ids['tail_duration']
    self.generate_ir = self.ids['generate_ir']
    self.save_button = self.ids['save_button']
    self.advanced_settings = self.ids['advanced_settings']
    self.sine_sweep_param = self.ids['sine_sweep_param']
    self.acoustic_param = self.ids['acoustic_param']
    self.play_button = self.ids['play_button']
    self.stop_audio_button = self.ids['stop_audio_button']
    self.sweep_counter = self.ids['sweep_counter']
    self.hide_button = self.ids['hide_button']
    
    self.record_state = False
    
    if platform == 'android':
        self.universal_sample_rate = 44100
    else:
        self.universal_sample_rate = 48000
    self.countdown_duration = 3
    self.full_scale_mV = 1
    
    self.min_freq = 10
    self.max_freq = 24000
    self.sweep_duration = 10
    self.fade_duration = 10
    
    self.IR_audio = None
    
    self.tab_state = 0
    
    self.graph_display = False
    
    self.IR_signal = None
    
    self.playSineSweep_t = None
    self.sine_sweep = None
    
    self.switch_active = True
    self.K = 1
    self.tail_duration = 2
    
    self.hide = True
    self.unit = 0

    self.generate_ir.bind(on_release=self.generateIRSignal)
    self.save_button.bind(on_release=self.saveFileCaller)
    self.tail_duration_text.bind(text=self.update_timer_duration_tail)
    self.sweep_counter.bind(text=self.update_timer_duration_K)

    self.recording = None
    self.sweep_signal = None
    self.window = "hann"
    
    self.frames = []
    self.mic = None
    
    self.stream = None
    self.micE = ""
    self.buf_size = 1024
    self.wave_write_done = False
    
    self.sweep_start_time = None
    self.delay = 0
    self.sweep_signal = None
    self.sweep_signal_K = None
    self.FT_unit, self.time_unit = 0,0
    
    self.current_voltage = None
    

    
    self.tab = 0
    self.box1 =self.ids['box1']
    self.box2 = self.ids['box2']
    self.box3= self.ids['box3']
    self.box4= self.ids['box4']
    self.box5= self.ids['box5']
    
    
    self.spacer1 =self.ids['spacer1']
    self.spacer2 = self.ids['spacer2']
    self.spacer3= self.ids['spacer3']
    self.spacer4= self.ids['spacer4']
    self.spacer5= self.ids['spacer5']
    
    self.display = self.ids['display']
    
    self.manual_stop = False
    
    self.error_list = []
    self.value_list = ["Countdown Duration","Min Frequency","Max Frequency","Sweep Duration","Fade Duration","Peak Input Voltage","Reverb Decay","Sweep Count"]
    
    self.sine_sweep_tab()
    
    
    self.timer_duration = self.K*(self.sweep_duration + self.tail_duration)
    
    
    self.energy = None
    self.peak_amp = None
    self.flatness = None
    self.K_value = None
    self.edt = None
    self.rt60 = None
    
    self.preload_sound()
    
    
    
        
  def startMeasurementClock(self):
    """
      Functionality:
          
      """
      
      
    try:
          if self.IR_audio != None:
              self.IR_audio.stop()
    except:
          pass
      
    if len(self.error_list) > 1:
        print(self.error_list)
        #self.display_label.text = f'ERROR:\n {len(self.error_list)}\n'
        wrong_values = [self.value_list[index] for index, _ in self.error_list]
        wrong_values_text = ', '.join(wrong_values)
        #error_messages_text = ", ".join([f'"{error_message}"' for _, error_message in self.error_list])
        self.display_label.text = f'Wrong Values Were Detected!\n{wrong_values_text} are Invalid!\n'
        return
    elif len(self.error_list) > 0:
        print(self.error_list)
        self.display_label.text = f'Wrong Value Was Detected!\n{self.value_list[self.error_list[-1][0]]} is Invalid!\n'
        #self.display_label.text += f'"{self.error_list[-1][1]}"'
        return
        
    
    if platform == 'android':
      print("Status: Requesting RECORD_AUDIO Permission")
      request_permissions([Permission.RECORD_AUDIO])

    if self.graph_display:
        self.display.clear_widgets()
      
        label = MDLabel(
        text="00:00",
        height=dp(100),
        halign="center",
        theme_text_color = 'Primary',
        font_size = '16sp'
        )
        self.display.add_widget(label)
        self.display_label = self.display.children[0]
        
        self.graph_display = False
        
    #print(self.K)
    self.countdown_duration_timer = self.countdown_duration
      
    self.display_label.text = f"Starting recording in: {self.countdown_duration} s"
    self.start_button.disabled = True
    self.play_button.disabled = True
    self.stop_audio_button.disabled = True
    self.stop_button.disabled = False
    self.stop_button.display_label = False
    #self.switch.disabled = True
    self.generate_ir.disabled = True
    Clock.schedule_interval(self.countdownUpdate, 1)
    
   
    
  def measurementClock(self):
    self.zero = 1  # Reset to 00:00
    self.mins = 0  # Reset the minutes Timer
    self.timer_duration = int(self.K*(self.sweep_duration + self.tail_duration))
    self.K_value = self.K

    if self.switch_active and (type(self.timer_duration) != int or (int(self.timer_duration) < 1)):
      self.display_label.text = 'ERROR: User value must be a positive integer!'
    elif self.switch_active and int(self.timer_duration) > 3600-1:
      self.display_label.text = 'ERROR: User value is too large! - (3599 s Maximimum)'
    else:
        
      print("Status: Generating Exp. Sine Sweep Array")
      self.display_label.text = 'Generating Exp. Sine Sweep Signal'
      self.sweep_signal_K = dsp.signal_ess(float(self.sweep_duration),self.universal_sample_rate,float(self.min_freq),float(self.max_freq),t0=self.fade_duration/1000,K=self.K,spacing=self.tail_duration,fade_type=self.window)
      self.sweep_signal = dsp.signal_ess(float(self.sweep_duration),self.universal_sample_rate,float(self.min_freq),float(self.max_freq),t0=self.fade_duration/1000,K=1,spacing=self.tail_duration,fade_type=self.window)
      
      self.display_label.text = 'Saving Exp. Sine Sweep File'
      print("Status: Saving Exp. Sine Sweep Array as wav")
      self.scaling_sweep = self.sweep_signal_K.export('sdcard/dsp_app/sweep.wav')
        
      if self.switch_active:
        self.duration = int(self.timer_duration)
        self.display_label.text = f"{self.duration // 60:02d}:{self.duration % 60:02d}"
      else:
        self.display_label.text = "00:00"
      
      Clock.schedule_interval(self.updateDisplay, 1)
      print("Status: Playing Sine Sweep")
    
      # BUTTON STATES
      
      print("Status: Initializing Recording")
      Clock.schedule_once(self.startRecording)
      #self.playSineSweep_t = threading.Thread(target=self.playSineSweep)
      #self.playSineSweep_t.start()
      
  def stopMeasurement(self):
      
    if self.playSineSweep_t != None:
      self.playSineSweep_t.join()
      self.playSineSweep_t = None
    
    Clock.unschedule(self.countdownUpdate)
    Clock.unschedule(self.poll_input_queue)
    Clock.unschedule(self.updateDisplay)
    Clock.unschedule(self.stopMeasurement)
    if platform == 'android' and self.mic!=None:
      Clock.unschedule(self.poll_input_queue)
      self.mic.stop()
      rec = wave.open("sdcard/dsp_app/signal.wav", 'wb')
      rec.setnchannels(self.mic.channels)
      rec.setsampwidth(2)
      rec.setframerate(self.universal_sample_rate)
      rec.writeframes(b''.join(self.frames))
      rec.close()
      self.generate_ir.disabled = False
      print("Status: Recording. .wav File was Sucessful!")
      
    elif platform == 'win' or platform == 'macosx' or platform == 'linux':
      Clock.unschedule(self.mic_pyaudio_update)
      if self.stream:
        self.stream.stop_stream()
        self.stream.close()
        self.stream = None
        self.p.terminate()
        
        rec = wave.open("sdcard/dsp_app/signal.wav", 'wb')
        rec.setnchannels(1)
        rec.setsampwidth(self.p.get_sample_size(pyaudio.paInt16))
        print(f"Sample Width:  {self.p.get_sample_size(pyaudio.paInt16)}")
        rec.setframerate(self.universal_sample_rate)
        rec.writeframes(b''.join(self.frames))
        rec.close()
        self.generate_ir.disabled = False
        self.wav_write_done = True
        print("Status: Recording. .wav File was Sucessful!")
        self.p = None
      else:
        if self.micE == "":
            print(f"Status: Recording .wav File was Unsucessful!\n       Exception: \"{self.micE}\"")
        else:
            print('Status: Recording .wav File was Unsucessful!\nNo exception was specified.')
        self.wav_write_done = False
    
    #BUTTON STATES
    if platform == 'android' and self.mic==None:
      if self.manual_stop == True:
          if self.record_state == True:
              self.display_label.text = 'Measurement Finished\n (User Input)'
              self.manual_stop = False
          else:
              self.display_label.text = 'Measurement Cancelled'
              self.manual_stop = False
      elif self.micE != "":
          self.display_label.text = f'Finished Measurement\n(ERROR: AUDIO STREAM WAS UNSUCESSFUL)\nException: \"{self.micE}\"'
      else:
          self.display_label.text = 'Finished Measurement\n(ERROR: AUDIO STREAM WAS UNSUCESSFUL)\nNo exception was specified.'
      self.generate_ir.disabled = True
    elif (platform == 'win' or platform == 'macosx' or platform == 'linux') and self.wav_write_done==False:
      if self.manual_stop == True:
          if self.record_state == True:
              self.display_label.text = 'Measurement Finished\n (User Input)'
              self.manual_stop = False
          else:
              self.display_label.text = 'Measurement Cancelled'
              self.manual_stop = False
      elif self.micE != "":
          self.display_label.text = f'Finished Measurement\n(ERROR: AUDIO STREAM WAS UNSUCESSFUL)\nException: \"{self.micE}\"'
      else:
          self.display_label.text = 'Finished Measurement\n(ERROR: AUDIO STREAM WAS UNSUCESSFUL)\nNo exception was specified.'
      self.generate_ir.disabled = True
    else:
      self.display_label.text = 'Finished Measurement'
      self.generate_ir.disabled = False
      self.manual_stop = False
    
    if self.sine_sweep != None:
        self.sine_sweep.stop()
    self.start_button.disabled = False
    self.stop_button.disabled = True
    self.record_state = False
    #self.switch.disabled = False
      
      
  def updateDisplay(self, dt):
    if not self.switch_active:
      if self.zero == 60:
        self.mins += 1
        self.zero = 0
          
      self.display_label.text = f"{self.mins:02d}:{self.zero:02d}"
      self.zero += 1
          
    else:
      if self.duration == 0:    
        self.stopMeasurement()
      else:
        self.duration -= 1
        self.display_label.text = f"{self.duration // 60:02d}:{self.duration % 60:02d}"
              
  def mic_callback(self,buf):
    #print('Recieved Sample Buffer: ', len(buf), " Bytes")
    self.frames.append(buf)
      
  def mic_pyaudio_update(self,*arg):
    data = self.stream.read(self.buf_size)
    #print('Recieved Sample Buffer: ', self.buf_size, " Bytes")
    self.frames.append(data)

  def startRecording(self, dt):
    
    if platform == 'android':
      # Request microphone permission here
      request_permissions([Permission.RECORD_AUDIO])
      try:
        self.record_state = True
        self.sine_sweep = SoundLoader.load('sdcard/dsp_app/sweep.wav')
        
        print("Status: Initializing 'mic' Object")
        self.frames = []
        
        if self.universal_sample_rate <= 44100:
            self.buf_size = 2048*2
        elif self.universal_sample_rate <= 48000:
            self.buf_size = 2048*4
        else:
            self.buf_size = 2048*8
            
        sample_rate = self.universal_sample_rate
        self.mic = get_input(callback = self.mic_callback, buffersize= self.buf_size)
        
        print("Status: Calling 'mic.start'")
        self.mic.start()
        
        self.rec_start_time = Clock.get_time()
        
        Clock.schedule_interval(self.poll_input_queue, self.buf_size/sample_rate)
      except Exception as e:
        self.record_state = False
        print("Error:", e)
        self.micE = e
    elif platform == 'win' or platform == 'macosx' or platform == 'linux':
      try:
        self.record_state = True
        self.sine_sweep = SoundLoader.load('sdcard/dsp_app/sweep.wav')
        
        self.p = pyaudio.PyAudio()
        self.frames = []
        
        if self.universal_sample_rate <= 44100:
            self.buf_size = 2048*2
        elif self.universal_sample_rate <= 48000:
            self.buf_size = 2048*4
        else:
            self.buf_size = 2048*8
            
        sample_format = pyaudio.paInt16
        channels = 1
        sample_rate = self.universal_sample_rate
        
        self.stream = self.p.open(format=sample_format,
              channels=channels,
              rate=sample_rate,
              frames_per_buffer=self.buf_size,
              input=True)
        
        self.rec_start_time = Clock.get_time()
        
        Clock.schedule_interval(self.mic_pyaudio_update, self.buf_size/sample_rate)
        
      except Exception as e:
        print("Error:", e)
        self.record_state = False
        self.micE = e
    else:
      print("Error: Recording is Not Supported for This Platform")
    if self.sine_sweep:
      self.sine_sweep.play()
      self.sweep_start_time = Clock.get_time()

    print(f"Delay: {self.delay*self.universal_sample_rate} samples")
    
  def poll_input_queue(self, dt):
    # Poll the input queue to trigger the callback
    self.mic.poll()
    
    
  def countdownUpdate(self, dt):
    self.countdown_duration_timer -= 1
    if self.countdown_duration_timer <= 0:
      Clock.unschedule(self.countdownUpdate)
      self.measurementClock()
    else:
      self.display_label.text = f"Starting recording in: {self.countdown_duration_timer} s"

   
  def generateIRSignal(self, *args):
    self.delay = self.sweep_start_time - self.rec_start_time
    self.display_label.text = 'Generating Impulse Response'
    
    
    Clock.schedule_once(self.IR_compute,0.1)
    
  def IR_compute(self,dt):
    print("Status: Generating IR_signal object")
    self.recording = dsp.signal_import('sdcard/dsp_app/signal.wav')
    print(f"Recording Sample Length: {len(self.recording.x)}\nRecording Time Length: {len(self.recording.x)/self.universal_sample_rate} s")
    try:
        self.IR_signal = dsp.signal_inv_reg_filter('impulse_response', self.recording, self.sweep_signal,self.delay,fs=self.recording.fs,reg_param=1e-9,K=self.K,sweep_T=self.sweep_duration+self.tail_duration)
    except:
        self.display_label.text = 'Impulse Reponse Could Not Be Generated'
        return
    
    print("Status: Cleaning Up Impulse Response (Trimming End)")
    self.IR_signal = dsp.ir_tail_cleanup(self.IR_signal)
    print("Status: Saving signal as WAV for playback")
    self.IR_signal.export("sdcard/dsp_app/ir_signal.wav")
    
    #self.IR_signal.flatness()
    #print(self.IR_signal.flat_score)
    """
    fig, axs = plt.subplots(2, figsize=(16, 6))  # Create two subplots side by side

    self.recording.freq_response()
    self.sweep_signal.freq_response()
    
    axs[0].plot(self.recording.f, self.recording.y)
    axs[0].set_title("Frequency Response of Recording")
    axs[0].set_xlabel("Frequency (Hz)")
    axs[0].set_ylabel("Amplitude (dB)")
    
    axs[1].plot(self.sweep_signal.f, self.sweep_signal.y)
    axs[1].set_title("Frequency Response of Sweep Signal")
    axs[1].set_xlabel("Frequency (Hz)")
    axs[1].set_ylabel("Amplitude (dB)")
    
    plt.tight_layout()  # Adjust subplots to fit into figure area.
    plt.show()
    """  
    
    self.computeMetrics()
    
    
    if self.tab == 1:
        self.acoustic_param_tab()
    
    self.play_button.disabled = False
    self.stop_audio_button.disabled = False
    print("Status: Plotting Impulse & Frequency Responses")
    self.save_button.disabled = False
    self.plotIR()

  def plotIR(self):
        self.IR_signal.freq_response(sens=self.full_scale_mV)

        dtu_red = '#990000'

        f = self.IR_signal.f
        if self.FT_unit == 1:
            H = self.IR_signal.y_mV
            self.current_voltage = self.full_scale_mV
        else:
            H = self.IR_signal.y

        positive_indices = np.where(f >= 0)[0]
        f_positive = f[positive_indices]
        H_positive = H[positive_indices]

        n = self.IR_signal.n
        if self.time_unit == 0:
            x = self.IR_signal.x
        else:
            self.current_voltage = self.full_scale_mV
            x = self.IR_signal.x * self.full_scale_mV
        fs = self.IR_signal.fs

        max_data_points = 1920*2
        
        downsample_factor = int(np.ceil(len(n) / max_data_points))

        if len(f_positive) > max_data_points:
            downsample_factor = int(np.ceil(len(f_positive) / max_data_points))
            f_downsampled = f_positive[::downsample_factor]
            H_downsampled = H_positive[::downsample_factor]
        else:
            f_downsampled = f_positive
            H_downsampled = H_positive
            

        if len(n) > max_data_points:
            peak_index = np.argmax(x)
            peak_negative_index = np.argmax(-x) 
        
            idx = list(range(0, len(n), downsample_factor))
            if peak_index not in idx:
                idx.append(peak_index)
                idx.append(peak_negative_index)
                
            idx = sorted(idx)
            
            n_downsampled = n[idx]
            x_downsampled = x[idx]
        else:
            n_downsampled = n
            x_downsampled = x
        
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 5), gridspec_kw={'height_ratios': [1, 1]},facecolor="#fafafa")

        ax1.plot(f_downsampled, H_downsampled, color=dtu_red)
        ax1.set_xlabel('Frequency (Hz)', fontsize=14)
        ax1.set_ylabel('Magnitude (dBFS)' if self.FT_unit == 0 else 'Magnitude (mV) - Log-Scale', fontsize=14)
        ax1.set_title('Frequency Response - H(f)', fontsize=16, color=dtu_red)
        ax1.grid(True)

        ax2.plot(n_downsampled / fs, x_downsampled, color=dtu_red)
        ax2.set_xlabel('Time [s]', fontsize=14)
        ax2.set_ylabel('Amplitude' if self.time_unit == 0 else 'Amplitude (mV)', fontsize=14)
        #ax2.set_ylim(-1, 1) if self.time_unit == 0 else ax2.set_ylim(-self.full_scale_mV, self.full_scale_mV)
        ax2.set_title('Time Domain Signal - h(t)', fontsize=16, color=dtu_red)
        ax2.grid(True)
        
        for ax in [ax1, ax2]:
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_color('#2f2f2f')
            ax.spines['bottom'].set_color('#2f2f2f')
            ax.xaxis.label.set_color('#2f2f2f')
            ax.yaxis.label.set_color('#2f2f2f')
            ax.tick_params(axis='x', colors='#2f2f2f')
            ax.tick_params(axis='y', colors='#2f2f2f')
            #ax.title.set_fontsize(18)
            #ax.title.set_weight('bold')
            ax.title.set_color(dtu_red)

        plt.tight_layout()
        self.display.clear_widgets()
        matplot = graph_subplot_widget.MatplotFigureSubplot()
        matplot.figure = fig
        
        self.display.add_widget(matplot)
        self.graph_display = True
        self.generate_ir.disabled = True
      
  def saveFile(self, signal, name, ir=False):
    """
    Functionality:
        Saves a wave file.
    """
    filename = self.ids['save_file_name'].text + "_" + name + ".wav"
    csv_filename = self.ids['save_file_name'].text + "_" + name + ".csv"

    if platform == 'android':
        documents_dir = os.path.join(primary_external_storage_path(), "Documents","DSPApp")
        if not os.path.exists(documents_dir):
            os.makedirs(documents_dir)
        path = os.path.join(documents_dir, filename)
        csv_path = os.path.join(documents_dir, csv_filename)
    else:
        path = os.path.join("sdcard", "dsp_app", filename)
        csv_path = os.path.join("sdcard", "dsp_app", csv_filename)

    print(f"Status: Saving IR to WAV file: {path}")

    try:
        with wave.open(path, 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(signal.fs)

            if ir:
                x = (signal.x / np.max(np.abs(signal.x)) * (2**15 - 1)).astype(np.int16)
                print(f"Status: Normalized IR to 16bit Int - Scaling Factor: {np.max(np.abs(signal.x))}")
            else:
                x = (signal.x * (2**15 - 1)).astype(np.int16)
                print(f"Status:Scaled signal to 16bit Int - Scaling Factor: {np.max(np.abs(signal.x))}")

            data = np.array(x, dtype=np.int16)
            wav_file.writeframes(data.tobytes())

        print(f"Status: File '{filename}' saved successfully!")

        print(f"Status: Saving File to CSV file: {csv_path}")
        with open(csv_path, 'w', newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(['Index', 'Value'])
            for i, value in enumerate(signal.x):
                writer.writerow([i, value])

        print(f"Status: File '{csv_filename}' saved successfully!")

    except Exception as e:
        print(f"Error: Saving IR failed! Exception: {e}")
        
  def saveFileCaller(self,*args):
      self.saveFile(self.IR_signal,"IR",ir=True)
      self.saveFile(self.recording,"Y")
      self.saveFile(self.sweep_signal,"SWEEP")  
      
      
  def advanced_settings_tab(self):
        print("Status: Advanced Settings Tab Selected")

        self.box1.clear_widgets()
        self.box1.add_widget(MDLabel(text='Sample Rate:', size_hint=(3/2, None), height=dp(40),font_size='12sp',theme_text_color= 'Secondary',font_style='Subtitle2',halign = 'center'))
        self.add_sample_rate_buttons(self.box1)

        self.box2.clear_widgets()
        self.box2.add_widget(MDLabel(text='Countdown Timer:', size_hint=(1/2, None), height=dp(40),font_size='12sp',theme_text_color= 'Secondary',font_style='Subtitle2',halign = 'center'))
        self.add_countdown_timer(self.box2)

        self.box3.clear_widgets()
        self.box3.add_widget(MDLabel(text='Freq. Domain Unit:', size_hint=(2/2, None), height=dp(40),font_size='12sp',theme_text_color= 'Secondary',font_style='Subtitle2',halign = 'center'))
        self.add_unit_FT_buttons(self.box3)

        self.box4.clear_widgets()
        self.box4.add_widget(MDLabel(text='Time Domain Unit:', size_hint=(2/2, None), height=dp(40),font_size='12sp',theme_text_color= 'Secondary',font_style='Subtitle2',halign = 'center'))
        self.add_unit_time_buttons(self.box4)

        self.box5.clear_widgets()
        self.box5.add_widget(MDLabel(text='Peak Input Voltage [mV]:', size_hint=(1/2, None), height=dp(40),font_size='12sp',theme_text_color= 'Secondary',font_style='Subtitle2',halign = 'center'))
        self.add_full_scale_mV_input(self.box5)
        
        self.unhide_tabs()
        self.hide = 1
        self.hide_button.icon = 'triangle-small-down'
        self.hide_button.text = 'Hide'

        self.advanced_settings.disabled = True
        self.acoustic_param.disabled = False
        self.sine_sweep_param.disabled = False
    
        self.tab = 2
        
  def acoustic_param_tab(self):
    print("Status: Acoustic Parameter Tab Selected")

    fs = f"{self.IR_signal.fs / 1000:.1f} kHz" if self.IR_signal else "N/A"
    length = f"{len(self.IR_signal.n) / self.IR_signal.fs:.2f} s" if self.IR_signal else "N/A"
    sine_sweeps = f"{self.K_value}" if self.K_value else "N/A"

    str_energy = f"{self.energy:.3e}" if self.energy else "N/A"
    str_peak_amp = f"{self.peak_amp:.3e}" if self.peak_amp else "N/A"
    if self.unit:
        str_energy = f"{self.energy * self.full_scale_mV**2:.3e} mV^2s" if self.energy else "N/A"
        str_peak_amp = f"{self.peak_amp * self.full_scale_mV:.3e} mV" if self.peak_amp else "N/A"

    str_edt = f"{self.edt:.2f} s" if self.edt else "N/A"
    str_rt60 = f"{self.rt60:.2f} s" if self.rt60 else "N/A"

    self.box1.clear_widgets()
    self.box1.add_widget(Widget(width=dp(10)))
    self.box1.add_widget(MDLabel(text=f'Sample Rate:\n{fs}', height=dp(40), font_size='12sp', theme_text_color='Secondary', font_style='Subtitle2', halign='center'))
    self.box1.add_widget(MDLabel(text='Signal Length:\n' + length, height=dp(40), font_size='12sp', theme_text_color='Secondary', font_style='Subtitle2', halign='center'))
    self.box1.add_widget(MDLabel(text='Sweep Count:\n' + sine_sweeps, height=dp(40), font_size='12sp', theme_text_color='Secondary', font_style='Subtitle2', halign='center'))
    self.box1.add_widget(Widget(width=dp(10)))

    self.box2.clear_widgets()
    self.box2.add_widget(Widget(width=dp(10)))
    self.box2.add_widget(MDLabel(text='Energy:\n' + str_energy, height=dp(40), font_size='12sp', theme_text_color='Secondary', font_style='Subtitle2', halign='center'))
    self.box2.add_widget(MDLabel(text='Peak Amplitude:\n' + str_peak_amp, height=dp(40), font_size='12sp', theme_text_color='Secondary', font_style='Subtitle2', halign='center'))
    self.box2.add_widget(Widget(width=dp(10)))

    self.box3.clear_widgets()
    self.box3.add_widget(Widget(width=dp(10)))
    self.box3.add_widget(MDLabel(text='EDT:\n' + str_edt, height=dp(40), font_size='12sp', theme_text_color='Secondary', font_style='Subtitle2', halign='center'))
    self.box3.add_widget(MDLabel(text='RT60:\n' + str_rt60, height=dp(40), font_size='12sp', theme_text_color='Secondary', font_style='Subtitle2', halign='center'))
    self.box3.add_widget(Widget(width=dp(10)))

    self.box4.clear_widgets()

    self.box5.clear_widgets()
    self.box5.add_widget(MDLabel(text='Units:', size_hint=(0.6, None), height=dp(40), font_size='12sp', theme_text_color='Secondary', font_style='Subtitle2', halign='center'))
    self.add_unit_buttons(self.box5)
    self.box5.add_widget(MDLabel(text='Peak Input Voltage [mV]:', size_hint=(0.6, None), height=dp(40), font_size='12sp', theme_text_color='Secondary', font_style='Subtitle2', halign='center'))
    self.add_full_scale_mV_input(self.box5)

    self.unhide_tabs()
    self.hide = 1
    self.hide_button.icon = 'triangle-small-down'
    self.hide_button.text = 'Hide'

    self.advanced_settings.disabled = False
    self.acoustic_param.disabled = True
    self.sine_sweep_param.disabled = False
    self.tab = 1


  def sine_sweep_tab(self):
        print("Status: Sine Sweep Tab Selected")

        self.box1.clear_widgets()
        self.box1.add_widget(MDLabel(text='Min Frequency [Hz]:', size_hint=(1/2, None), height=dp(40),font_size='12sp',theme_text_color= 'Secondary',font_style='Subtitle2',halign = 'center'))
        self.add_min_freq_input(self.box1)

        self.box2.clear_widgets()
        self.box2.add_widget(MDLabel(text='Max Frequency [Hz]:', size_hint=(1/2, None), height=dp(40),font_size='12sp',theme_text_color= 'Secondary',font_style='Subtitle2',halign = 'center'))
        self.add_max_freq_input(self.box2)

        self.box3.clear_widgets()
        self.box3.add_widget(MDLabel(text='Sweep Duration  [s]:', size_hint=(1/2, None), height=dp(40),font_size='12sp',theme_text_color= 'Secondary',font_style='Subtitle2',halign = 'center'))
        self.add_sweep_duration_input(self.box3)
        
        self.box4.clear_widgets()
        self.box4.add_widget(MDLabel(text='Window Type:', size_hint=(3/2, None), height=dp(40),theme_text_color= 'Secondary',font_style='Subtitle2',halign = 'center'))
        self.add_window_buttons(self.box4)

        self.box5.clear_widgets()
        self.box5.add_widget(MDLabel(text='Window Fade Time [ms]:', size_hint=(1/2, None), height=dp(40),font_size='12sp',theme_text_color= 'Secondary',font_style='Subtitle2',halign = 'center'))
        self.add_fade_duration_input(self.box5)
        
        self.unhide_tabs()
        self.hide = 1
        self.hide_button.icon = 'triangle-small-down'
        self.hide_button.text = 'Hide'
       

        self.advanced_settings.disabled = False
        self.acoustic_param.disabled = False
        self.sine_sweep_param.disabled = True
        self.tab = 0
        
  def unhide_tabs(self):
        self.display.spacing = dp(0)
              
        self.box1.height = dp(40)
        self.box2.height = dp(40)
        self.box3.height = dp(40)
        self.box4.height = dp(40)
        self.box5.height = dp(40)
        
        self.spacer1.height = dp(15)
        self.spacer2.height = dp(15)
        self.spacer3.height = dp(15)
        self.spacer4.height = dp(15)
        self.spacer5.height = dp(15)
        

    
        
  def hide_tabs(self):
      if self.hide:
          self.display.spacing = dp(0)
          
          self.box1.clear_widgets()
          self.box1.height = dp(0)
          self.box2.clear_widgets()
          self.box2.height = dp(0)
          self.box3.clear_widgets()
          self.box3.height = dp(0)
          self.box4.clear_widgets()
          self.box4.height = dp(0)
          self.box5.clear_widgets()
          self.box5.height = dp(0)
          
          self.spacer1.height = dp(0)
          self.spacer2.height = dp(0)
          self.spacer3.height = dp(0)
          self.spacer4.height = dp(0)
          self.spacer5.height = dp(0)
          
          self.advanced_settings.disabled = False
          self.acoustic_param.disabled = False
          self.sine_sweep_param.disabled = False
          
          self.hide = 0
          
          self.hide_button.icon = 'triangle-small-up'
          self.hide_button.text = 'Unhide'
      else:
         self.hide_button.icon = 'triangle-small-down'
         self.hide_button.text = 'Hide'
         self.hide = 1
         if self.tab == 0:
            self.sine_sweep_tab()
         elif self.tab == 1:
            self.acoustic_param_tab()
         else:
            self.advanced_settings_tab()
      
      

  def update_parent_widgets(self, parent, new_widget):
        if parent:
            parent.clear_widgets()
            parent.add_widget(new_widget)

  def add_sample_rate_buttons(self, parent):
        self.button_44_1kHz = MDFillRoundFlatButton(
            text='44.1 kHz',
            size_hint=(1, None),
            height=dp(40),
            on_release=lambda x: self.set_sample_rate(44100),
            md_bg_color=(153/255, 0, 0, 1),
            font_size="14sp",
            theme_text_color= 'Custom',
            text_color= (1, 1, 1, 1)
        )

        self.button_48kHz = MDFillRoundFlatButton(
            text='48 kHz',
            size_hint=(1, None),
            height=dp(40),
            on_release=lambda x: self.set_sample_rate(48000),
            md_bg_color = (153/255, 0, 0, 1),
            font_size = "14sp",
            theme_text_color= 'Custom',
            text_color= (1, 1, 1, 1)
        )

        self.button_96kHz = MDFillRoundFlatButton(
            text='96 kHz',
            size_hint=(1, None),
            height=dp(40),
            on_release=lambda x: self.set_sample_rate(96000),
            md_bg_color = (153/255, 0, 0, 1),
            font_size = "14sp",
            theme_text_color= 'Custom',
            text_color= (1, 1, 1, 1)
        )

        if self.universal_sample_rate == 44100:
            self.button_44_1kHz.disabled = True
            self.button_48kHz.disabled = False
            self.button_96kHz.disabled = False
        elif self.universal_sample_rate == 48000:
            self.button_44_1kHz.disabled = False
            self.button_48kHz.disabled = True
            self.button_96kHz.disabled = False
        elif self.universal_sample_rate == 96000:
            self.button_44_1kHz.disabled = False
            self.button_48kHz.disabled = False
            self.button_96kHz.disabled = True
        else:
            self.button_44_1kHz.disabled = False
            self.button_48kHz.disabled = False
            self.button_96kHz.disabled = False

        parent.add_widget(self.button_44_1kHz)
        parent.add_widget(self.button_48kHz)
        parent.add_widget(self.button_96kHz)

  def add_unit_FT_buttons(self, parent):
        self.button_FT_dBFS = MDFillRoundFlatButton( 
            text='dBFS',
            size_hint=(1, None),
            height=dp(40),
            on_release=lambda x: self.set_FT_unit(0),
            md_bg_color = (153/255, 0, 0, 1),
            font_size = "14sp",
            theme_text_color= 'Custom',
            text_color= (1, 1, 1, 1)
        )
        self.button_FT_mV = MDFillRoundFlatButton(
            text='mV - Log-Scale',
            size_hint=(1, None),
            height=dp(40),
            on_release=lambda x: self.set_FT_unit(1),
            md_bg_color = (153/255, 0, 0, 1),
            font_size = "14sp",
            theme_text_color= 'Custom',
            text_color= (1, 1, 1, 1)
        )

        if self.FT_unit == 0:
            self.button_FT_dBFS.disabled = True
            self.button_FT_mV.disabled = False
        else:
            self.button_FT_dBFS.disabled = False
            self.button_FT_mV.disabled = True

        parent.add_widget(self.button_FT_dBFS)
        parent.add_widget(self.button_FT_mV)
        
        
  def add_unit_buttons(self, parent):
        self.button_full_scale = MDFillRoundFlatButton( 
            text='Full Scale',
            size_hint=(1, None),
            height=dp(40),
            on_release=lambda x: self.set_unit(0),
            md_bg_color = (153/255, 0, 0, 1),
            font_size = "14sp",
            theme_text_color= 'Custom',
            text_color= (1, 1, 1, 1)
        )
        self.button_mV = MDFillRoundFlatButton(
            text='Metric',
            size_hint=(1, None),
            height=dp(40),
            on_release=lambda x: self.set_unit(1),
            md_bg_color = (153/255, 0, 0, 1),
            font_size = "14sp",
            theme_text_color= 'Custom',
            text_color= (1, 1, 1, 1)
        )

        if self.unit == 0:
            self.button_full_scale.disabled = True
            self.button_mV.disabled = False
        else:
            self.button_full_scale.disabled = False
            self.button_mV.disabled = True

        parent.add_widget(self.button_full_scale)
        parent.add_widget(self.button_mV)
        
  def add_window_buttons(self, parent):
        self.button_dirichlet = MDFillRoundFlatButton( 
            text='Dirichlet',
            size_hint=(1, None),
            height=dp(40),
            on_release=lambda x: self.set_window(0),
            md_bg_color = (153/255, 0, 0, 1),
            font_size = "14sp",
            theme_text_color= 'Custom',
            text_color= (1, 1, 1, 1)
        )
        self.button_hann = MDFillRoundFlatButton(
            text='Hann',
            size_hint=(1, None),
            height=dp(40),
            on_release=lambda x: self.set_window(1),
            md_bg_color = (153/255, 0, 0, 1),
            font_size = "14sp",
            theme_text_color= 'Custom',
            text_color= (1, 1, 1, 1)
        )
        self.button_triangular = MDFillRoundFlatButton(
            text='Triangular',
            size_hint=(1, None),
            height=dp(40),
            on_release=lambda x: self.set_window(2),
            md_bg_color = (153/255, 0, 0, 1),
            font_size = "14sp",
            theme_text_color= 'Custom',
            text_color= (1, 1, 1, 1)
        )

        if self.window == "hann":
            self.button_dirichlet.disabled = False
            self.button_hann.disabled = True
            self.button_triangular.disabled = False
            
            self.box5.clear_widgets()
            self.box5.add_widget(MDLabel(text='Window Fade Time [ms]:', size_hint=(1/2, None), height=dp(40),font_size='12sp',theme_text_color= 'Secondary',font_style='Subtitle2',halign = 'center'))
            self.add_fade_duration_input(self.box5)
        elif self.window == "tri":
            self.button_dirichlet.disabled = False
            self.button_hann.disabled = False
            self.button_triangular.disabled = True
            
            self.box5.clear_widgets()
            self.box5.add_widget(MDLabel(text='Window Fade Time [ms]:', size_hint=(1/2, None), height=dp(40),font_size='12sp',theme_text_color= 'Secondary',font_style='Subtitle2',halign = 'center'))
            self.add_fade_duration_input(self.box5)
        else:
            self.box5.clear_widgets()
            self.button_dirichlet.disabled = True
            self.button_hann.disabled = False
            self.button_triangular.disabled = False

        parent.add_widget(self.button_dirichlet)
        parent.add_widget(self.button_hann)
        parent.add_widget(self.button_triangular)

  def add_unit_time_buttons(self, parent):
        self.button_time_dBFS = MDFillRoundFlatButton(
            text='Full-Scale',
            size_hint=(1, None),
            height=dp(40),
            on_release=lambda x: self.set_time_unit(0),
            md_bg_color = (153/255, 0, 0, 1),
            font_size = "14sp",
            theme_text_color= 'Custom',
            text_color= (1, 1, 1, 1)
        )
        self.button_time_mV = MDFillRoundFlatButton(
            text='mV',
            size_hint=(1, None),
            height=dp(40),
            on_release=lambda x: self.set_time_unit(1),
            md_bg_color = (153/255, 0, 0, 1),
            font_size = "14sp",
            theme_text_color= 'Custom',
            text_color= (1, 1, 1, 1)
        )

        if self.time_unit == 0:
            self.button_time_dBFS.disabled = True
            self.button_time_mV.disabled = False
        else:
            self.button_time_dBFS.disabled = False
            self.button_time_mV.disabled = True

        parent.add_widget(self.button_time_dBFS)
        parent.add_widget(self.button_time_mV)

  def add_countdown_timer(self, parent):
    self.text_input_countdown_timer = MDTextField(
        text=str(self.countdown_duration),
        size_hint=(1, None),
        height=dp(40),
        halign='center',
        multiline=False,
        icon_right="counter",
        helper_text="Seconds before measurement begins (positive int)"
    )
    self.text_input_countdown_timer.bind(text=self.update_countdown_duration)
    parent.add_widget(self.text_input_countdown_timer)
    if 0 in [error[0] for error in self.error_list]:
      Clock.schedule_once(lambda dt: setattr(self.text_input_countdown_timer, 'error', True))

  def add_min_freq_input(self, parent):
    self.min_freq_input = MDTextField(
        text=str(self.min_freq),
        size_hint=(1, None),
        height=dp(40),
        halign='center',
        multiline=False,
        icon_right="sine-wave",
        helper_text="Starting sweep frequency (float)"
    )
    self.min_freq_input.bind(text=self.update_min_freq)
    parent.add_widget(self.min_freq_input)
    
    if 1 in [error[0] for error in self.error_list]:
      Clock.schedule_once(lambda dt: setattr(self.min_freq_input, 'error', True))


  def add_max_freq_input(self, parent):
    self.max_freq_input = MDTextField(
        text=str(self.max_freq),
        size_hint=(1, None),
        height=dp(40),
        halign='center',
        multiline=False,
        icon_right="sine-wave",
        helper_text="Ending sweep frequency (float)"
    )
    self.max_freq_input.bind(text=self.update_max_freq)
    parent.add_widget(self.max_freq_input)
    if 2 in [error[0] for error in self.error_list]:
      Clock.schedule_once(lambda dt: setattr(self.max_freq_input, 'error', True))

  def add_sweep_duration_input(self, parent):
    self.sweep_duration_input = MDTextField(
        text=str(self.sweep_duration),
        size_hint=(1, None),
        height=dp(40),
        halign='center',
        multiline=False,
        icon_right="timer-sync-outline",
        helper_text="Duration of single sweep (float)"
    )
    self.sweep_duration_input.bind(text=self.update_sweep_duration)
    parent.add_widget(self.sweep_duration_input)
    if 3 in [error[0] for error in self.error_list]:
      Clock.schedule_once(lambda dt: setattr(self.sweep_duration_input, 'error', True))

  def add_fade_duration_input(self, parent):
    self.fade_duration_input = MDTextField(
        text=str(self.fade_duration),
        size_hint=(1, None),
        height=dp(40),
        halign='center',
        multiline=False,
        icon_right="chart-bell-curve-cumulative",
        helper_text="Fade time of window - max is half of sweep duration (float)"
    )
    self.fade_duration_input.bind(text=self.update_fade_duration)
    parent.add_widget(self.fade_duration_input)
    if 4 in [error[0] for error in self.error_list]:
      Clock.schedule_once(lambda dt: setattr(self.fade_duration_input, 'error', True))

  def add_full_scale_mV_input(self, parent):
    self.full_scale_mV_input = MDTextField(
        text=str(self.full_scale_mV),
        size_hint=(1, None),
        height=dp(40),
        halign='center',
        multiline=False,
        icon_right="lightning-bolt-outline",
        on_text_validate=self.validate_voltage
    )
    self.full_scale_mV_input.bind(text=self.update_full_scale_mV)
    
    if self.tab == 1:
        self.full_scale_mV_input.helper_text = "ADC's Peak Voltage - Reference Voltage (float)"
    else:
        self.full_scale_mV_input.helper_text = "ADC's Peak Voltage (float)"
    parent.add_widget(self.full_scale_mV_input)
    if 5 in [error[0] for error in self.error_list]:
      Clock.schedule_once(lambda dt: setattr(self.full_scale_mV_input, 'error', True))
    
  def update_countdown_duration(self, instance, value):
      try:
          self.countdown_duration = int(value)
          
          if self.countdown_duration < 0:
              self.text_input_countdown_timer.error = True
              self.errorList(0, True, reason="Value cannot be negative!")
          else:
              self.errorList(0, False)
      except:
          self.text_input_countdown_timer.error = True
          self.errorList(0, True, reason="Value is invalid!")
  
  def update_min_freq(self, instance, value):
    try:
        self.min_freq = float(value)
        if self.min_freq <= 0:
            self.min_freq_input.error = True
            self.errorList(1, True, reason="Value must be positive!")
            self.update_min_freq("", str(self.max_freq))
        elif self.max_freq <= self.min_freq:
            self.min_freq_input.error = True
            self.max_freq_input.error = True
            self.update_min_freq("", str(self.max_freq))
            self.errorList(1, True, reason="Min Frequency must be smaller than Max Frequency!")
        else:
            if self.max_freq <= 0:
                self.max_freq_input.error = True
                self.update_min_freq("", str(self.min_freq))
                self.errorList(2, True, reason="Value must be positive!")
            else:
                self.update_min_freq("", str(self.min_freq))
                self.max_freq_input.error = False
                self.errorList(2, False)
            self.min_freq_input.error = False
            self.errorList(1, False)
    except:
        self.min_freq_input.error = True
        self.errorList(1, True, reason="Value is invalid!")

  def update_max_freq(self, instance, value):
    try:
        self.max_freq = float(value)
        if self.max_freq <= 0:
            self.max_freq_input.error = True
            self.update_min_freq("", str(self.min_freq))
            self.errorList(2, True, reason="Value must be positive!")
        elif self.max_freq <= self.min_freq:
            self.max_freq_input.error = True
            self.min_freq_input.error = True
            self.errorList(2, True, reason="Max Frequency must be larger than Min Frequency!")
        else:
            if self.min_freq <= 0:
                self.min_freq_input.error = True
                self.errorList(1, True, reason="Value must be positive!")
            else:
                self.min_freq_input.error = False
                self.errorList(1, False)
            self.update_min_freq("", str(self.min_freq))
            self.max_freq_input.error = False
            self.errorList(2, False)
    except:
        self.max_freq_input.error = True
        self.errorList(2, True, reason="Value is invalid!")

  def update_sweep_duration(self, instance, value):
    try:
        self.sweep_duration = float(value)
        if self.sweep_duration <= 0:
            self.sweep_duration_input.error = True
            self.errorList(3, True, reason="Value must be positive!")
        else:
            self.sweep_duration_input.error = False
            self.errorList(3, False)
    except:
        self.sweep_duration_input.error = True
        self.errorList(3, True, reason="Value is invalid!")

  def update_fade_duration(self, instance, value):
    try:
        self.fade_duration = float(value)
        if self.fade_duration <= 0:
            self.fade_duration_input.error = True
            self.errorList(4, True, reason="Value must be positive!")
        elif self.fade_duration / 1000 > self.sweep_duration / 2:
            self.fade_duration_input.error = True
            self.errorList(4, True, reason="Value cannot exceed half of Sweep Duration")
        else:
            self.fade_duration_input.error = False
            self.errorList(4, False)
    except:
        self.fade_duration_input.error = True
        self.errorList(4, True, reason="Value is invalid!")

  def update_full_scale_mV(self, instance, value):
    try:
        self.full_scale_mV = float(value)
        if np.isnan(self.full_scale_mV) or np.isinf(self.full_scale_mV):
            self.full_scale_mV_input.error = True
            self.errorList(5, True, reason="Value must be real!")
        elif self.full_scale_mV <= 0:
            self.full_scale_mV_input.error = True
            self.errorList(5, True, reason="Value must be larger than 0!")
        else:
            self.full_scale_mV_input.error = False
            self.errorList(5, False)
    except:
        self.full_scale_mV_input.error = True
        self.errorList(5, True, reason="Value is invalid!")

  def update_timer_duration_tail(self, instance, value):
    try:
        self.duration_tail = int(value)
        if self.duration_tail < 0:
            self.tail_duration_text.error = True
            self.errorList(6, True, reason="Value cannot be negative!")
        elif self.duration_tail > 100:
            self.tail_duration_text.error = True
            self.errorList(6, True, reason="Value is too large!")
        else:
            self.tail_duration_text.error = False
            self.errorList(6, False)
    except:
        self.tail_duration_text.error = True
        self.errorList(6, True, reason="Value is invalid!")

  def update_timer_duration_K(self, instance, value):
    print(value)
    try:
        self.K = int(value)
        if self.K < 1:
            self.sweep_counter.error = True
            self.errorList(7, True, reason="Number of Sweeps must be at least 1!")
        elif self.K > 100:
            self.sweep_counter.error = True
            self.errorList(7, True, reason="Number of Sweeps is Too Large!")
        else:
            self.sweep_counter.error = False
            self.errorList(7, False)
    except Exception as e:
        print(e,value)
        self.sweep_counter.error = True
        self.errorList(7, True, reason="Value is invalid!")
                
      
                
  def set_sample_rate(self, sample_rate):
        self.universal_sample_rate = sample_rate
        print(f"Status: Sample Rate set to: {self.universal_sample_rate}")
        if sample_rate == 44100:
            self.button_44_1kHz.disabled = True
            self.button_48kHz.disabled = False
            self.button_96kHz.disabled = False
            
        elif sample_rate == 48000:
            self.button_44_1kHz.disabled = False
            self.button_48kHz.disabled = True
            self.button_96kHz.disabled = False
        elif sample_rate == 96000:
            self.button_44_1kHz.disabled = False
            self.button_48kHz.disabled = False
            self.button_96kHz.disabled = True
        else:
            self.button_44_1kHz.disabled = False
            self.button_48kHz.disabled = False
            self.button_96kHz.disabled = False
            
  def set_FT_unit(self,unit_idx):
      self.FT_unit = unit_idx
      
      if self.FT_unit == 0:
            self.button_FT_dBFS.disabled = True
            self.button_FT_mV.disabled = False
      else:
            self.button_FT_dBFS.disabled = False
            self.button_FT_mV.disabled = True
            
      if self.graph_display:
          self.plotIR()
            
  def set_unit(self,unit_idx):
      self.unit = unit_idx
      
      if self.unit == 0:
            self.button_full_scale.disabled = True
            self.button_mV.disabled = False
      else:
            self.button_full_scale.disabled = False
            self.button_mV.disabled = True
      self.acoustic_param_tab()
          
  def set_time_unit(self,unit_idx):
      self.time_unit = unit_idx
      
      if self.time_unit == 0:
            self.button_time_dBFS.disabled = True
            self.button_time_mV.disabled = False
      else:
            self.button_time_dBFS.disabled = False
            self.button_time_mV.disabled = True
      if self.graph_display:
          self.plotIR()
          
  def set_window(self,window_idx):
      if window_idx == 0:
          self.window = "dirichlet"
          self.button_dirichlet.disabled = True
          self.button_hann.disabled = False
          self.button_triangular.disabled =False
          
          self.box5.clear_widgets()
      elif window_idx == 1:
          self.window = "hann"
          self.button_dirichlet.disabled = False
          self.button_hann.disabled = True
          self.button_triangular.disabled =False
          
          self.box5.clear_widgets()
          self.box5.add_widget(MDLabel(text='Window Fade Time [ms]:', size_hint=(1/2, None), height=dp(40),font_size='12sp',theme_text_color= 'Secondary',font_style='Subtitle2',halign = 'center'))
          self.add_fade_duration_input(self.box5)
      else:
          self.window = "tri"
          self.button_dirichlet.disabled = False
          self.button_hann.disabled = False
          self.button_triangular.disabled =True
          
          self.box5.clear_widgets()
          self.box5.add_widget(MDLabel(text='Window Fade Time [ms]:', size_hint=(1/2, None), height=dp(40),font_size='12sp',theme_text_color= 'Secondary',font_style='Subtitle2',halign = 'center'))
          self.add_fade_duration_input(self.box5)
          
  def validate_voltage(self,*args):
      if self.graph_display and self.current_voltage != self.full_scale_mV and (self.time_unit != 0 or self.FT_unit != 0):
          self.plotIR()
      if self.tab == 1:
          self.acoustic_param_tab()
      
        


  def playIR(self):
      try:
          if self.IR_audio != None:
              self.IR_audio.stop()
          self.IR_audio = SoundLoader.load('sdcard/dsp_app/ir_signal.wav')
          self.IR_audio.play()
      except:
          print("Error: Could not play IR file.")
          
  def stopIR(self):
      try:
          if self.IR_audio != None:
              self.IR_audio.stop()
      except:
          pass

  def computeMetrics(self):
    T = len(self.IR_signal.n)/self.IR_signal.fs
    self.energy = np.sum(np.abs(self.IR_signal.x)**2,axis=0)*T
    self.peak_amp = np.max(np.abs(self.IR_signal.x))
    self.rt60, self.edt = dsp.compute_rt(self.IR_signal)
    
  def errorList(self, element, add, reason=""):
        if add: 
            if element not in [error[0] for error in self.error_list]:
                self.error_list.append([element, reason])
        else:
            self.error_list = [[e, r] for e, r in self.error_list if e != element]
            
  def stopButton(self):
      self.manual_stop = True
      self.stopMeasurement()
      
  def preload_sound(self):
    x = np.zeros(100, dtype=np.float64)
    dummy_signal = dsp.signal("dummy", x, self.universal_sample_rate)
    
    dummy_filename = 'sdcard/dsp_app/dummy_signal.wav'
    dummy_signal.export(dummy_filename)
    
    sound = SoundLoader.load(dummy_filename)
    
    if sound:
        sound.play()
        sound.stop()

      
      
if __name__ == '__main__':
  DSPApp().run()
