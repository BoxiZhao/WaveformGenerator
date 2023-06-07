# WaveformGenerator.py
# Boxi @ 2023.6.6

import numpy as np
import re
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, SpanSelector, RangeSlider, TextBox

# --- USER SETTINGS -----------------------

ac_level = 1;
window_size = 12
step_min = 0.01
smooth_rate = 0.2
save_path = 'waveform.txt'

# --- END SETTINGS ------------------------

choose_n = [11, 21, 51]
choose_width = [0.04, 0.03, 0.01]
choose_space = [0.068, 0.034, 0.0136]
choose_startpoint = [0.245, 0.25, 0.26]

# Define initial parameters
n_slider = choose_n[ac_level];
n_gap = n_slider - 1;
y_value = [0] * n_slider
x_index = list(np.array(range(0, n_slider)) / n_gap)

sel_min, sel_max = 0, 0
opt_st, opt_ed = 0, 1

# Create the figure and the line that we will manipulate
fig, ax = plt.subplots(figsize=(window_size, window_size * 0.4))
fig.canvas.manager.set_window_title('Waveform Generator')
line, = ax.plot(x_index, y_value)
plt.ylim((0, 1))
plt.xlim((0, 1))
ax.set_xticks(np.linspace(0, 1.001, int(n_gap / 2) + 1))
plt.grid(linestyle='dashed', alpha=0.5)
fig.subplots_adjust(left=0.263, right=0.945, bottom=0.54, top = 0.92)

# Button Settings
interp_ax = fig.add_axes([0.04, 0.71, 0.06, 0.08])
button_interp = Button(interp_ax, 'INTERP', hovercolor='0.8', color='1')
smooth_ax = fig.add_axes([0.04, 0.58, 0.06, 0.08])
button_smooth = Button(smooth_ax, 'SMOOTH', hovercolor='0.8', color='1')
reset_ax = fig.add_axes([0.04, 0.84, 0.06, 0.08])
button_reset = Button(reset_ax, 'RESET', hovercolor='0.8', color='1')
save_ax = fig.add_axes([0.04, 0.45, 0.06, 0.08])
button_save = Button(save_ax, 'SAVE', hovercolor='0.8', color='1')
axcmd = fig.add_axes([0.04, 0.08, 0.06, 0.15])
cmd = TextBox(axcmd, label='', color='1', hovercolor='1')
axcmd.set_title('-- CMD --', fontsize=10)

axsp = fig.add_axes([0.18, 0.1, 0.04, 0.78])
sldsp = Slider(ax=axsp, valmin=0, valmax=1, valinit=0, valstep=step_min, track_color='0.95', label='Range\nModifier', orientation="vertical")
axrg = fig.add_axes([0.13, 0.1, 0.04, 0.78])
sldrg = RangeSlider(ax=axrg, valmin=0, valmax=1, valinit=(0,1), valstep=step_min, track_color='0.95', label='Output\nPosition', orientation="vertical")

# Functions
def normalpos(pos):
	global opt_st
	global opt_ed
	return (pos - opt_st) / (opt_ed - opt_st)

def clip(val):
	return min(max(0, val), 1)

def out(str):
	return int(str) < 0 or int(str) >= n_slider

def getrange(min_sel=3):
	global sel_min
	global sel_max
	nml_max = normalpos(sel_max)
	nml_min = normalpos(sel_min)
	if (nml_max - nml_min) * n_gap <= min_sel - 1:
		return
	n_st = int(np.ceil(nml_min * n_gap))
	n_ed = int(np.floor(nml_max * n_gap))
	return n_st, n_ed

# Make a vertically oriented slider to control the amplitude
axs, slds = [], []
for i in range(n_slider):
	axt = fig.add_axes([choose_startpoint[ac_level] + choose_space[ac_level] * i, 0.1, choose_width[ac_level], 0.35])
	sldt = Slider(ax=axt, valmin=0, valmax=1, valinit=0, valstep=step_min, label=str(i), track_color='0.95', orientation="vertical")
	axs.append(axt)
	slds.append(sldt)

# The function to be called anytime a slider's value changes
def update(val):
	for i in range(n_slider):
		if line.get_ydata()[i] != slds[i].val:
			print("UPD " + str(i) + ' ' + str(slds[i].val))
	line.set_ydata([slds[i].val for i in range(n_slider)])
	fig.canvas.draw_idle()

# register the update function with each slider
for i in range(n_slider):
	slds[i].on_changed(update)

# Output Range Selector
def rsupdate(val):
	global opt_st
	global opt_ed
	opt_st = val[0]
	opt_ed = val[1]
	ax.set_xticks(np.linspace(opt_st, opt_ed + 0.00001, int(n_gap / 2) + 1))
	ax.set_xlim((opt_st, opt_ed))
	line.set_xdata(np.linspace(opt_st, opt_ed + 0.00001, n_slider))
	print("OPT " + str(opt_st) + ' ' + str(opt_ed))
	fig.canvas.draw_idle()
sldrg.on_changed(rsupdate)

# Range Modifier
def onselect(vmin, vmax):
	global sel_min
	global sel_max
	vmin = max(0, vmin)
	vmax = min(1, vmax)
	sel_min = vmin
	sel_max = vmax + 0.001
	print("SEL " + str(vmin) + ' ' + str(vmax))

rectprops = dict(facecolor='salmon', alpha=0.2)
span = SpanSelector(ax, onselect, 'horizontal', interactive=True, props=rectprops)

def makerangeupdate(n_st, n_ed, val):
	for i in range(n_st, n_ed + 1):
		slds[i].set_val(val)
	print("RUP " + str(n_st) + ' ' + str(n_ed) + ' ' + str(val))
def rangeupdate(val):
	n_st, n_ed = getrange(1)
	makerangeupdate(n_st, n_ed, sldsp.val)
sldsp.on_changed(rangeupdate)

# Create a Button for interpolation.
def makeinterp(n_st, n_ed):
	dval = (slds[n_ed].val - slds[n_st].val) / (n_ed - n_st)
	for i in range(n_st + 1, n_ed):
		slds[i].set_val(int((slds[n_st].val + dval * (i - n_st)) / step_min) * step_min)
	line.set_ydata([slds[i].val for i in range(n_slider)])
	print("ITP " + str(n_st) + ' ' + str(n_ed))
def interp(event):
	n_st, n_ed = getrange()
	makeinterp(n_st, n_ed)
button_interp.on_clicked(interp)

# Create a Button to make the waveform smooth.
def makesmooth(n_st, n_ed):
	for i in range(n_st + 1, n_ed):
		slds[i].set_val(int(((slds[i - 1].val + slds[i + 1].val) * 0.5 * smooth_rate + slds[i].val * (1 - smooth_rate)) / step_min) * step_min)
	line.set_ydata([slds[i].val for i in range(n_slider)])
	print("SMO " + str(n_st) + ' ' + str(n_ed))
	fig.canvas.draw_idle()
def smooth(event):
	n_st, n_ed = getrange()
	makesmooth(n_st, n_ed)
button_smooth.on_clicked(smooth)

# Create a Button to reset the sliders to initial values.
def makereset():
	print("RST")
	sldsp.reset()
	sldrg.reset()
	for i in range(n_slider):
		slds[i].reset()
def reset(event):
	makereset()
button_reset.on_clicked(reset)

# Create a Button to save the waveform.
def makesave():
	print("SAV", end=' ')
	print(line.get_ydata())
	with open(save_path,'w',encoding = 'utf-8') as f:
		if opt_st != 0:
			f.write("0 0\n")
			f.write(str(line.get_xdata()[0] - 0.001) + " 0\n")
		for i in range(n_slider):
			# f.write(str((i / (n_slider - 1)) * (opt_ed - opt_st) + opt_st) + ' ' + str(line.get_ydata()[i]) + '\n')
			f.write(str(line.get_xdata()[i]) + ' ' + str(line.get_ydata()[i]) + '\n')
		if opt_ed != 1:
			f.write(str(line.get_xdata()[n_slider - 1] + 0.001) + " 0\n")
			f.write("1 0\n")
def save(event):
	makesave()
button_save.on_clicked(save)

# Create a Textbox as command line
def submit(expression):
	text_split = cmd.text.upper().strip().split(' ')
	cmd.set_val('')
	argv = [word for word in text_split if word.strip() != '']
	if len(argv) == 0:
		return
	if argv[0] == 'UPD' and len(argv) > 2:
		if out(argv[1]):
			return
		slds[int(argv[1])].set_val(clip(float(argv[2])))
	elif argv[0] == 'RUP' and len(argv) > 3:
		if out(argv[1]) or out(argv[2]):
			return
		makerangeupdate(min(int(argv[1]), int(argv[2])), max(int(argv[1]), int(argv[2])), clip(float(argv[3])))
	elif argv[0] == 'SMO' and len(argv) > 2:
		if out(argv[1]) or out(argv[2]):
			return
		makesmooth(min(int(argv[1]), int(argv[2])), max(int(argv[1]), int(argv[2])))
	elif argv[0] == 'ITP' and len(argv) > 2:
		if out(argv[1]) or out(argv[2]):
			return
		makeinterp(min(int(argv[1]), int(argv[2])), max(int(argv[1]), int(argv[2])))
	elif argv[0] == 'OPT' and len(argv) > 2:
		if min(float(argv[1]), float(argv[2])) < 0 or max(float(argv[1]), float(argv[2])) > 1:
			return
		sldrg.set_val([min(float(argv[1]), float(argv[2])), max(float(argv[1]), float(argv[2]))])
	elif argv[0] == 'RST':
		makereset()
	elif argv[0] == 'SAV':
		makesave()
	return
cmd.on_submit(submit)

plt.show()
