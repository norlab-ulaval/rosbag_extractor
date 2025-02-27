import pandas as pd
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.animation import FuncAnimation
import numpy as np
from scipy.spatial.transform import Rotation as R
import matplotlib.pyplot as plt
from compute_tf import Tfquery  
import pathlib
from tqdm import tqdm

class TfVisualizer():

    def __init__(self):
        
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111, projection='3d')
        self.ani = None
        self.maximum = [0,0,0]
        self.minimum = [0,0,0]
    def identify_xyz_min_max(self, minimum, maximum, data):

        max_z = data["data"]['z'].max()
        max_y = data["data"]['y'].max()
        max_x = data["data"]['x'].max()

        if max_x > maximum[0]:
            maximum[0] = max_x
        if max_y > maximum[1]:
            maximum[1] = max_y
        if max_z > maximum[2]:
            maximum[2] = max_z

        min_z = data["data"]['z'].min()
        min_y = data["data"]['y'].min()
        min_x = data["data"]['x'].min()

        if min_x < minimum[0]:
            minimum[0] = min_x
        if min_y < minimum[1]:
            minimum[1] = min_y
        if min_z < minimum[2]:
            minimum[2] = min_z
                    

        return minimum,maximum
    def load_data(self,path_to_folder):
        """This function load data and extract the general timestamp to travel assuming that all df share the same timestamp index.

        Args:
            path_to_folder (_type_): _description_
            tfa_name (_type_): _description_

        Raises:
            ValueError: _description_
        """

        
        if not isinstance(path_to_folder,pathlib.Path):
            path_to_folder = pathlib.Path(path_to_folder)
        path_to_folder = pathlib.Path(path_to_folder)
        if path_to_folder.is_file():
            raise ValueError("the path needs to point to a folder containing all results")
        
        
        self.reference_frame = path_to_folder.stem
        

        dico_data = {}
        
        general_timestamp_recovered = False

        maximum = [0,0,0]
        minimum = [0,0,0]   

        for path in path_to_folder.iterdir():
            
            self.tfa_name =  path.stem.split("_in_")[0]
            if path.suffix not in [".csv"]:
                continue
            data = {}
            data["data"] = pd.read_csv(path,index_col="timestamp")
            data["frame_name"] =  self.tfa_name 
            dico_data[path.stem] = data
            #print(data["frame_name"])

            if not general_timestamp_recovered:
                general_timestamp_recovered = True
                self.timestamp_to_iterate = data["data"].index.to_numpy()
                
            self.identify_xyz_min_max( minimum, maximum, data)

                
        self.data = dico_data  
        self.path_to_folder = path_to_folder
        self.maximum = maximum
        self.minimum = minimum

    def set_x_y_z_lim(self, scale=1.1):
        
        self.ax.set_xlim([self.minimum[0]*scale, self.maximum[0]*scale])
        self.ax.set_ylim([self.minimum[1]*scale, self.maximum[1]*scale])
        self.ax.set_zlim([self.minimum[2]*scale, self.maximum[2]*scale])


    def update_one_frame(self, data,frame_name):
        
        x = data['x']
        y = data['y']
        z = data['z']
        qx = data['q_x']
        qy = data['q_y']
        qz = data['q_z']
        qw = data['q_w']
        
        self.ax.scatter(x, y, z, color='b', s=self.marker_size)
        
        r = R.from_quat([qx, qy, qz, qw],scalar_first=False)
        
        scale = self.arrow_scale   # Define the scale for the arrows
        
        direction = r.apply([1, 0, 0])
        self.ax.quiver(x, y, z, direction[0], direction[1], direction[2], color='r', length=scale, normalize=True)
        
        direction = r.apply([0, 1, 0])
        self.ax.quiver(x, y, z, direction[0], direction[1], direction[2], color='g', length=scale, normalize=True)
        
        direction = r.apply([0, 0, 1])
        self.ax.quiver(x, y, z, direction[0], direction[1], direction[2], color='b', length=scale, normalize=True)
        
        self.ax.text(x, y, z, frame_name, color='black', zorder=5)

    def update_animation(self, num):
        self.ax.clear()
        self.set_x_y_z_lim( scale=1.1)
        self.ax.set_xlabel('X')
        self.ax.set_ylabel('Y')
        self.ax.set_zlabel('Z')
        for key, values in self.data.items():
            
            timestamp = self.timestamp_to_iterate[num]
            data = values["data"].loc[timestamp]
            self.update_one_frame(data,values["frame_name"])
            

        data = {"x":0,"y":0,"z":0,"q_x":0,"q_y":0,"q_z":0,"q_w":1}
        
        self.update_one_frame(data,self.reference_frame)
        self.ax.set_title(f"Frame at timestamp {timestamp*10e-9}")
    def create_animation(self, save_results=False, arrow_scale=1,marker_size=1,camera_view=False,max_iter=0):
        """Create the animation of the tf frames in the 3D space.

        To have an interactive animation, set save_results to False.

        Args:
            save_results (bool, optional): Instead of an animation, create and save a video of the tf. Defaults to False.
            camera_view (bool, optional): Change the default view of the animation to fit the classic camera frame where z goes through the screen, x to the right and y downward . Defaults to False.
            max_iter (int, optional): if == 0, save all the frames. Only in save mod to verify and debug. Defaults to 0.
            arrow_scale (int, optional): scale parameter for the size of the arrow. Defaults to 1.
            marker_size (int, optional): scale parameter for the size of the arrow.. Defaults to 1.
        """
        self.set_x_y_z_lim(scale=1.1)
        self.pause =False
        self.arrow_scale = arrow_scale
        self.marker_size = marker_size 
        self.camera_view = camera_view
        if self.camera_view:
                self.ax.view_init(elev=-90, azim=0,roll=270)
            

        if save_results:
            # Create a progress bar
            if max_iter!=0:
                progress_bar = tqdm(total=max_iter, desc="Saving animation", unit="frame")
            else:
                progress_bar = tqdm(total=len(self.timestamp_to_iterate), desc="Saving animation", unit="frame")
            
            def update_and_progress(num):
                self.update_animation(num)
                progress_bar.update(1)
            
            if max_iter!=0:
                self.ani = FuncAnimation(self.fig, update_and_progress, 
                    frames=max_iter, interval=np.median(np.diff(self.timestamp_to_iterate)))
            else:
                self.ani = FuncAnimation(self.fig, update_and_progress, 
                    frames=len(self.timestamp_to_iterate), interval=np.median(np.diff(self.timestamp_to_iterate)))
            # Set the view to look in the positive z direction if camera_view is set to 'z_positive'
            
            # Save the animation as a video file
            video_path = self.path_to_folder / "animation.mp4"
            self.ani.save(video_path, writer='ffmpeg', fps=30)
            
            # Close the progress bar
            progress_bar.close()
        else:
            def update_and_pause(num):
                self.update_animation(num)
            #plt.pause(0.1)  # Pause to allow for keyboard interaction
            
            self.ani = FuncAnimation(self.fig, update_and_pause, 
                frames=len(self.timestamp_to_iterate), interval=0)
            
            def on_key(event):
                if event.key == ' ':
                    self.ani.event_source.start()
                    self.pause = not self.pause
                    print(f"Pause: {self.pause}")
                    if self.pause:
                        self.ani.event_source.stop()
                    elif self.pause == False:
                        self.ani.event_source.start()
                    
            
            self.fig.canvas.mpl_connect('key_press_event', on_key)
        
            plt.show()


if __name__ == "__main__":
    path_ = pathlib.Path("/media/nicolassamson/ssd_NS/wilah/extracted_results/tf")
    path_ = pathlib.Path("/media/nicolassamson/ssd_NS/wilah/extracted_results/tf/requested_tf/zedx_left_camera_optical_frame")
    visualizer = TfVisualizer()
    visualizer.load_data(path_)
    visualizer.create_animation(save_results=True,camera_view=True,max_iter=10)
