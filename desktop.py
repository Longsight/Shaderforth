'''
Plasma Shader
=============

This shader example have been taken from http://www.iquilezles.org/apps/shadertoy/
with some adapation.

This might become a Kivy widget when experimentation will be done.
'''

import os, sys
from compiler import Compiler
from kivy.clock import Clock
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.core.window import Window
from kivy.graphics import RenderContext
from kivy.properties import StringProperty

# This header must be not changed, it contain the minimum information from Kivy.
header = '''
#ifdef GL_ES
precision highp float;
#endif

/* Outputs from the vertex shader */
varying vec4 frag_color;
varying vec2 tex_coord0;

/* uniform texture samplers */
uniform sampler2D texture0;
'''

# Plasma shader
plasma_shader = header + '''
uniform vec3 iResolution;
uniform float iGlobalTime;

void main(void)
{
   float x = gl_FragCoord.x;
   float y = gl_FragCoord.y;
   float mov0 = x+y+cos(sin(iGlobalTime)*2.)*100.+sin(x/100.)*1000.;
   float mov1 = y / iResolution.y / 0.2 + iGlobalTime;
   float mov2 = x / iResolution.x / 0.2;
   float c1 = abs(sin(mov1+iGlobalTime)/2.+mov2/2.-mov1-mov2+iGlobalTime);
   float c2 = abs(sin(c1+sin(mov0/1000.+iGlobalTime)+sin(y/40.+iGlobalTime)+sin((x+y)/100.)*3.));
   float c3 = abs(sin(c2+cos(mov1+mov2+c2)+cos(mov2)+sin(x/1000.)));
   gl_FragColor = vec4( c1,c2,c3,1.0);
}
'''

class ShaderWidget(FloatLayout):

	# property to set the source code for fragment shader
	fs = StringProperty(None)

	def __init__(self, **kwargs):
		# Instead of using Canvas, we will use a RenderContext,
		# and change the default shader used.
		self.canvas = RenderContext()

		# call the constructor of parent
		# if they are any graphics object, they will be added on our new canvas
		super(ShaderWidget, self).__init__(**kwargs)

		# We'll update our glsl variables in a clock
		Clock.schedule_interval(self.update_glsl, 1 / 60.)

	def on_fs(self, instance, value):
		self.shaderfn = value
		self.time_last = os.path.getmtime(self.shaderfn)
		try:
			value = Compiler(file(value, 'r').read().decode('utf-8'), False, False).code
		except:
			print 'Shaderforth failure'
			import traceback
			traceback.print_exc()
			return
		print value
		value = header + value

		# set the fragment shader to our source code
		shader = self.canvas.shader
		old_value = shader.fs
		shader.fs = value
		if not shader.success:
			shader.fs = old_value
			print 'Shader compilation failed (GLSL)'
			#raise Exception('failed')

	def update_glsl(self, *largs):
		self.canvas['iGlobalTime'] = Clock.get_boottime()
		self.canvas['iResolution'] = list(map(float, self.size)) + [0.0]
		# This is needed for the default vertex shader.
		self.canvas['projection_mat'] = Window.render_context['projection_mat']

		mtime = os.path.getmtime(self.shaderfn)
		if mtime != self.time_last:
			#print 'foo!'
			self.on_fs(self, self.shaderfn)
			self.time_last = mtime

class DesktopApp(App):
	def build(self):
		self.title = 'Shaderforth Live -- ' + sys.argv[1]
		return ShaderWidget(fs=sys.argv[1])

if __name__ == '__main__':
	DesktopApp().run()
