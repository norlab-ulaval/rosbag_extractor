import yaml
import pandas
import numpy 
from scipy.spatial.transform import Rotation 
import pathlib 
import treelib
import pandas as pd 
import numpy as np 
from tqdm import tqdm

def extract_paths(tree):
    paths = []

    def recurse(node, path):
        path.append(node.tag)

        successors = node.successors(tree.identifier)
        if successors == []:
            paths.append(path[:])
        
        
        for child in successors:
            recurse(tree[child], path)
            
            if path[:] not in paths:
                paths.append(path[:])
        path.pop()

    root = tree.get_node(tree.root)
    recurse(root, [])
    return paths

def reindex_dataframe(df, new_index,col_to_use_as_index='time'):
        """
        Reindex a DataFrame using a new index from a Series and interpolate the data using the most recent data.

        Parameters:
        df (pd.DataFrame): The original DataFrame with a 'time' column.
        new_index (pd.Series): The new index to be used for the DataFrame.

        Returns:
        pd.DataFrame: A new DataFrame with the same data but reindexed and interpolated.
        """
        if col_to_use_as_index not in df.columns:
            raise ValueError("The DataFrame must contain a 'time' column.")
        
        new_df = df.copy()
        new_df.set_index(col_to_use_as_index, inplace=True, drop=False)
        #print(new_df.head(5))
        new_df = new_df.reindex(new_index, method='ffill')
        #print(new_df.head(5))
        return new_df

class Tfquery():

    def __init__(self, path_to_results_folder,tf_tree_file = "combined_tf_tree.yaml",debug=False):
        """Create a Tfquery object that will allow to compute the tf between two frames. 
        The creation of the object will load all the tf data, compute the stats about the tf,
        and save the tf tree in ../../tf_analysis/tf_tree.txt.

        Args:
            path_to_results_folder (_type_): path to th tf/tf_requested/<frame_of_reference folder>
            tf_tree_file (str, optional): yaml file that contains child:parent information for tree construction. Defaults to "combined_tf_tree.yaml".
            debug (bool, optional): _description_. Defaults to False.
        """
        if isinstance(path_to_results_folder,str):
            path_to_results_folder = pathlib.Path(path_to_results_folder)
        self.path_to_results_folder = path_to_results_folder
        self.path_to_yaml_tree = path_to_results_folder/"tf_analysis"/tf_tree_file

        with open(self.path_to_yaml_tree, "r") as file:
            tree_dico  = yaml.safe_load(file)
            self.tf_tree = treelib.Tree.from_map(tree_dico)
            self.tf_tree.save2file(self.path_to_results_folder/"tf_analysis"/"tf_tree.txt")
        self.path_from_a_to_b = []
        self.tf_minimum_rostime = ""
        self.tf_minimum_time = ""
        self.highest_rate_tf = ""
        self.dico_tf_computed = {}

        self.dico_tf_computed = {}
        
        # create folder
        self.path_to_requested_tf = self.path_to_results_folder/"requested_tf"
        if not self.path_to_requested_tf.exists():
            self.path_to_requested_tf.mkdir()
        
        self.path_to_repeated_tf = self.path_to_results_folder/"same_timestamp_tf"
        if not self.path_to_repeated_tf.exists():
            self.path_to_repeated_tf.mkdir()
        
        self.path_tf_analysis = self.path_to_results_folder/"tf_analysis"
        if not self.path_tf_analysis.exists():
            self.path_tf_analysis.mkdir()

        self.get_all_unique_tf()
        self.load_all_tf(debug=debug)
        self.compute_tf_stats(debug=debug)
        self.compute_time_stats(debug = debug)
        self.extract_timestamp_of_reference()

    def get_all_unique_tf(self):

        all_path_to_leaves = self.tf_tree.paths_to_leaves()
        unique_list = []
        for path_to_leaf in all_path_to_leaves:
            unique_list.extend(path_to_leaf)
        
        self.unique_tf = unique_list

        print(self.unique_tf)
        test =1 

    def get_path_from_tf_a_to_b(self,tfa,tfb,debug=True):
        """Compute the transform path to follow in the tree to go from tf a to tf b

        Args:
            tfa (_type_): Start = Name of the tf that you get when you print it
            tfb (_type_): End = Name of the tf that you get when you print it
            debug (bool, optional): _description_. Defaults to True.

        Raises:
            ValueError: Bad tfa
            ValueError: Bad tfb

        Returns:
            _type_: list_that express the path to transform b in a 
        """
        
        all_path =  extract_paths(self.tf_tree)

        path_to_a = []
        path_to_b = []


        for i,path in enumerate(all_path):

            if tfa == path[-1]: 
                path_to_a = path
            elif tfb == path[-1]:
                path_to_b = path
            
        

        if tfa == self.tf_tree.root:
            path_to_b.reverse()
            path_from_a_to_b = path_to_b
            path_from_a_to_b.pop(-1)
            self.reverse_tf = [True] * len(path_from_a_to_b) 
            
        elif tfb == self.tf_tree.root:
            
            path_from_a_to_b = path_to_a
            path_from_a_to_b.pop(0)
            self.reverse_tf = [False] * len(path_from_a_to_b) 
        else:
            if path_to_b == []:
                raise (f"No path between the root {path} and tfa was found")
            elif path_to_a == []:
                raise ValueError("No path between the root and tfb was found")


            common_elements = list(filter(lambda x: x in path_to_a, path_to_b))[-1] 
            path_a_sub = path_to_a[path_to_a.index(common_elements)+1:]
            path_b_sub = path_to_b[path_to_b.index(common_elements)+1:]
            path_a_sub.reverse()
            path_from_a_to_b = path_a_sub + path_b_sub
            path_from_a_to_b.reverse()
            self.reverse_tf =  [True] * len(path_b_sub) + [False] * len(path_a_sub)


        if debug:
            print(path_to_a)
            print(path_to_b)
            print(path_a_sub)
            print(path_from_a_to_b)

        if tfa == "upperpassive":
            print(1)

        self.path_from_a_to_b = path_from_a_to_b
        
        self.name_tfa_in_tfb = tfa+"_in_"+tfb
        self.name_tfb_in_tfa = tfb+"_in_"+tfa
        
        if self.path_from_a_to_b == []:
            raise ValueError("The path from a to b is empty")

       
        
    def load_the_essential_dataset(self,extension = ".csv",debug=True):
        """Load all necessary csv for the shortest path conversion in the dictionnary

        Args:
            extension (str, optional): The format of the file used. Defaults to ".csv".
            debug (bool, optional): to debug. Defaults to True.

        Raises:
            ValueError: _description_
        """
        if self.path_from_a_to_b == []:
            raise ValueError("Ypou need to call the method get_path_from_tf_a_to_b before calling this method")
        
        dico_data = {}
        for tf, reverse in zip(self.path_from_a_to_b,self.reverse_tf):
            
            if tf == self.tf_tree.root:
                dict_ = self.transform_from_matrix_to_record(np.eye(4))
                dict_["timestamp"] = 0
                dict_["ros_time"] = 0
                data = pd.DataFrame.from_records([dict_])
                dico_data[tf] = {"data":data, "info":{"tf":tf,"static":True}}
            else:
                path = self.path_to_results_folder/(tf+extension)
                df = pd.read_csv(path)
                dico_data[tf] = {"data":df, "info":{"tf":tf,"reverse":reverse}}
            #print(dico_data)


        self.dico_data = dico_data
        
    def load_all_tf(self,extension = ".csv",debug=True):
        """Load all necessary csv for the shortest path conversion in the dictionnary

        Args:
            extension (str, optional): The format of the file used. Defaults to ".csv".
            debug (bool, optional): to debug. Defaults to True.

        Raises:
            ValueError: _description_
        """
        
        dico_data = {}
        for tf in self.unique_tf:
            if tf == self.tf_tree.root:
                dict_ = self.transform_from_matrix_to_record(np.eye(4))
                dict_["timestamp"] = 0
                dict_["ros_time"] = 0
                data = pd.DataFrame.from_records([dict_])
                dico_data[tf] = {"data":data, "info":{"tf":tf,"static":True}}
            else:
            
                path = self.path_to_results_folder/(tf+extension)
                df = pd.read_csv(path)
                dico_data[tf] = {"data":df, "info":{"tf":tf}}

        self.dico_data = dico_data

    def compute_time_stats(self,debug = False,info=False):
        """Compute the minimum time and the maximum time for the tf"""

        minimimum_time = 10**12
        minimum_rostime = 10**12
        self.maximum_time_ros = 10**20
        self.maximum_time = 10**20

        for tf, df in self.dico_data.items():
            
            if tf == self.tf_tree.root:
                continue
            if df["info"]["static"] == False:
                df =df["data"]

                if minimimum_time < df["timestamp"].iloc[0]:
                    delta_time = df["timestamp"].iloc[0] - minimimum_time
                    minimimum_time = df["timestamp"].iloc[0]

                    if debug:
                        print(f"The new determining tf is : {tf}")
                        print(f"New minimum time : {minimimum_time}")
                        print(f"Delta time:  {delta_time}" )
                    
                if minimum_rostime < df["ros_time"].iloc[0]:
                    
                    delta_time = df["ros_time"].iloc[0] - minimum_rostime
                    minimum_rostime = df["ros_time"].iloc[0]
                    if debug:
                        #print(minimum_rostime)
                        print(f"The new determining tf is : {tf}")
                        print(f"New minimum ros_time : {minimum_rostime}")
                        print(f"Delta time:  {delta_time}" )
                    
                if self.maximum_time > df["timestamp"].iloc[-1]:
                    self.maximum_time = df["timestamp"].iloc[-1]
                if self.maximum_time > df["ros_time"].iloc[0]:
                    self.maximum_time_ros = df["ros_time"].iloc[-1]
            
        self.minimum_rostime = minimum_rostime # 
        self.minimum_time = minimimum_time

        if info:
            debug_msg = "_"*10 + f"Compute time stats for {self.name_tfa_in_tfb}" + "_"*10
            print(debug_msg)
            print(f"Minimum time is : {self.minimum_time}")
            print(f"Minimum rostime is : {self.minimum_rostime}")
            print(f"Maximum time is : {self.maximum_time}")
            print(f"Maximum ros time is : {self.maximum_time_ros}")
            print(f"Delta time is : {self.maximum_time - self.minimum_time}")
            print(f"Delta rostime is : {self.maximum_time_ros - self.minimum_rostime}")
            print("_"*len(debug_msg) )
        
    def compute_tf_stats(self, static_nb_pub_treshold = 5,debug=False):
        """Goal to identify the highest rate tf

        Args:
            static_nb_pub_treshold (int, optional): _description_. Defaults to 5.
            debug (bool, optional): _description_. Defaults to False.
        """
        
        list_data = []
        
        highest_rate_tf = ""
        highest_rate = 0

        nbr_static= 0 
        for tf, dico_data in self.dico_data.items():
            
            dico_line_with_id =self.dico_data[tf]["info"] 
            if dico_data["data"].shape[0] < static_nb_pub_treshold:
                dico_line_with_id["static"] = True
                nbr_static +=1 
            else:
                dico_line_with_id["static"] = False
                
                
                dico_line_with_id["ros_time_median_rate"] = (1/ (dico_data["data"].ros_time.diff() *10e-9)).median()
                dico_line_with_id["timestamp_median_rate"] = (1/ (dico_data["data"].timestamp.diff() *10e-9)).median()
                dico_line_with_id["ros_time_std_rate"] = (1/ (dico_data["data"].ros_time.diff() *10e-9)).std()
                dico_line_with_id["timestamp_std_rate"] = (1/ (dico_data["data"].timestamp.diff() *10e-9)).std()
                dico_line_with_id["ros_time_average_rate_s"] = (1/ (dico_data["data"].ros_time.diff() *10e-9)).mean()
                dico_line_with_id["timestamp_average_rate_s"] = (1/ (dico_data["data"].timestamp.diff() *10e-9)).mean()
                
                if dico_line_with_id["timestamp_median_rate"] > highest_rate:
                    highest_rate = dico_line_with_id["timestamp_median_rate"]
                    highest_rate_tf = tf
                
                
            dico_data["info"]["pub_count"] = dico_data["data"].shape[0]
            dico_line_with_id["tf"] = tf
            list_data.append(dico_line_with_id)

        
        df_results = pd.DataFrame.from_records(list_data)
        df_results.to_csv(self.path_tf_analysis/"stats_about_tf.csv")
        self.highest_rate_tf = highest_rate_tf

        df = df_results.loc[df_results["tf"] == self.highest_rate_tf]
            
        
        if debug:
            debug_msg = "_"*10 + f"Compute tf stats for {self.name_tfa_in_tfb}" + "_"*10
            print(debug_msg)
            print(df.iloc[0])
            print("_"*len(debug_msg) )
    

    def extract_timestamp_of_reference(self):

        timestamp_col = self.dico_data[self.highest_rate_tf]["data"]["timestamp"]
        self.timestamp_ref = timestamp_col[(timestamp_col >= self.minimum_time) & (timestamp_col < self.maximum_time)]
        
        #print(self.timestamp_ref.describe())

    def extract_tf_from_df(self,target_epoch_time, df, linear_interpolation =False,debug= True):
        """Extract the closest precedent_tf

        Args:
            target_epoch_time (_type_): _description_
            df (_type_): _description_
            linear_interpolation (bool, optional): To dev with linear interpolation on xyz and slerp on q1 to q4.
            debug (bool, optional): _description_. Defaults to True.

        Returns:
            _type_: _description_
        """
        #if linear_interpolation:
        #    # Perform interpolation
        #    tf_raw_data = df.reindex(df.index.union([target_epoch_time])).interpolate(method='linear').loc[target_epoch_time]
        #else:
        # Find the closest previous time to the target time (the maximum timestamp that's <= target_epoch_time)
        closest_previous_time = df.index[df.index <= target_epoch_time].max()
        # Get the corresponding row for the closest previous time
        tf_raw_data = df.loc[closest_previous_time]

        # Extracting the tf
        rot_matrix = Rotation.from_quat([tf_raw_data.q_x,tf_raw_data.q_y,tf_raw_data.q_z,tf_raw_data.q_w],scalar_first=False).as_matrix()
        tf_matrix = np.eye(4)
        tf_matrix[:3,:3] = rot_matrix
        tf_matrix[:3,3] = np.array([tf_raw_data.x,tf_raw_data.y,tf_raw_data.z])
        
        
        if debug:    
            print(f"\n Linear interpoaltion is {linear_interpolation}, taking values at epoch time", target_epoch_time, ":")
            print(tf_raw_data)
            print(f" Here is the rotation matrix obtained: \n {rot_matrix}")
            print(f" Here is the tf matrix obtained: \n {tf_matrix}")

        return tf_matrix
        

        
    def transform_from_matrix_to_record(self,matrix):
        """Transform the matrix in the records format for pandas.Dataframe.from_records()

        Args:
            matrix (_type_): _description_

        Returns:
            _type_: _description_
        """
        rotation_quat = Rotation.from_matrix(matrix[:3,:3]).as_quat(scalar_first=False)

        record = {"x":matrix[0,3], "y":matrix[1,3], "z":matrix[2,3] , "q_x":rotation_quat[0],
                "q_y":rotation_quat[1], "q_z":rotation_quat[2], "q_w":rotation_quat[3]}
        return record
        
        

    def redefine_index_on_all_data(self,column):
        for tf in self.dico_data.keys():
            self.dico_data[tf]["data"].set_index(column,inplace=True, drop=False)

    
        
    
    def verify_if_tf_are_all_static(self):

        nb_static = 0 
        for tf in self.path_from_a_to_b:
            
            if self.dico_data[tf]["info"]["static"]:
                nb_static +=1
        
        if nb_static == len(self.path_from_a_to_b):

            return True
        
        else:
            return False
        
    def compute_tf_static(self):

        tf_final = np.eye(4)
        minimum_time = 0
        for tf_name,reversed in zip(self.path_from_a_to_b,self.reverse_tf): 
            tf_data = self.dico_data[tf_name]
            tf_raw_data = tf_data["data"].iloc[0]
            rot_matrix = Rotation.from_quat([tf_raw_data.q_x,tf_raw_data.q_y,tf_raw_data.q_z,tf_raw_data.q_w],scalar_first=False).as_matrix()
            tf_matrix = np.eye(4)
            tf_matrix[:3,:3] = rot_matrix
            tf_matrix[:3,3] = np.array([tf_raw_data.x,tf_raw_data.y,tf_raw_data.z])

            if reversed:
                tf_matrix = np.linalg.inv(tf_matrix)
            tf_final  = tf_final @ tf_matrix

            if minimum_time < tf_data["data"]["timestamp"].iloc[0]:
                minimum_time = tf_data["data"]["timestamp"].iloc[0]

        tf_final_a_in_b = tf_final
        tf_final_b_in_a = np.linalg.inv(tf_final)
        
        record = self.transform_from_matrix_to_record(tf_final_a_in_b)
        record["timestamp"] = minimum_time
        self.dico_tf_computed[self.name_tfb_in_tfa] = pd.DataFrame.from_records([record])
        
        record_reverse = self.transform_from_matrix_to_record(np.linalg.inv(tf_final_b_in_a))
        record_reverse["timestamp"] = minimum_time
        self.dico_tf_computed[self.name_tfa_in_tfb] = pd.DataFrame.from_records([record_reverse])
        
    def compute_tf(self,using_ros_time = False,linear_interpolation = False,debug = False,info=False):
        """Assuming 
        """
        # Define the minimum time
        
        if using_ros_time:
            time = self.minimum_rostime
            time_col = "ros_time"
        else:
            time = self.minimum_time
            time_col = "timestamp"
        self.delta_time = self.maximum_time - time
        # readjust the index appropriate for the time column selected
        self.redefine_index_on_all_data(time_col)

        list_tf_a_in_b = []
        list_tf_b_in_a = []
        next_time = 0
        if info:
            print(f"Starting interpolation refering to tf : {self.highest_rate_tf}")
            print(f"Starting time is : {time}")
            print(f"Maximum time is : {self.maximum_time}")
        starting_time = time

        last_progress = -1
        
        while time < self.maximum_time:
            
            final_tf = np.eye(4)  
            # Extract all tf
            for tf_name,reversed in zip(self.path_from_a_to_b,self.reverse_tf): 
                
                # Extract tf data
                tf_data = self.dico_data[tf_name]
                
                if tf_data["info"]["static"] == True:
                    # Find the closest index in the 'values' column
                    
                    if "tf_num" not in tf_data.keys(): #Load a tf
                        
                        tf = self.extract_tf_from_df(time, tf_data["data"], linear_interpolation =linear_interpolation,debug= debug)
                        if reversed:
                            tf = np.linalg.inv(tf)
                        self.dico_data[tf_name]["tf_num"] = tf
                        
                    else:
                        tf = tf_data["tf_num"]
                else:
                    
                    tf = self.extract_tf_from_df(time, tf_data["data"], linear_interpolation =linear_interpolation,debug= debug)
                    
                    if reversed:
                        tf = np.linalg.inv(tf)

                

                # Multiply the tf 
                
                final_tf = final_tf @ tf
                
                
                

            if debug:
                    print("_"*5 + f"Tf at that time {(time-starting_time)} s"+ "_"*5)
                    print(final_tf)
                    test = 1 
    
            # Save the tf with the rostime in quat
            record = self.transform_from_matrix_to_record(final_tf)
            record["timestamp"] = time
            
            
            record_reverse = self.transform_from_matrix_to_record(np.linalg.inv(final_tf))
            record_reverse["timestamp"] = time

            ##### The tf are defined child to parent, to reduce the calculation, 
            # we compute the reverse tf and then reverse it.  
            list_tf_a_in_b.append(record)
            list_tf_b_in_a.append(record_reverse)
            # Actualize the time 
            #print(time)

            # find the next time 
            
            
            
           
            #print(next_time)
            progress = int(((time - self.minimum_time)/ self.delta_time * 100))

            if progress%20 ==0.0 and progress != last_progress:
                last_progress = progress
                print(f"progress = {progress} %")
            next_time = self.timestamp_ref.loc[self.timestamp_ref>time].min()#  1731521634057477888
            
                #raise ValueError(f"next_time {next_time}")
            time = next_time
        #print(list_tf_a_in_b)
        
        self.dico_tf_computed[self.name_tfa_in_tfb] = pd.DataFrame.from_records(list_tf_a_in_b)
        #print("\n"*3,len(list_tf_a_in_b),"\n"*3)
        # Computed reverse tf 

        self.dico_tf_computed[self.name_tfb_in_tfa] = pd.DataFrame.from_records(list_tf_b_in_a)
        
    
    def save_tf(self,adjust_index_to_time_ref=True):
        """Save all tf previusly requested in the tf/tf_requested folder. 
        Each frame of reference will have its own folder in which the corresponding tf will be saved.
        each csv will be named <frame of reference>_in_<frame of reference>.csv
        
        Args:
            adjust_index_to_time_ref (bool, optional): _description_. Defaults to True.
        """
        

        for tf_name, df_tf in self.dico_tf_computed.items():
            
            
            
            folder_for_frame = self.path_to_requested_tf/tf_name.split("_in_")[1]
            if not folder_for_frame.exists():
                folder_for_frame.mkdir()
            path_to_save = folder_for_frame/(tf_name+".csv")
            

            if adjust_index_to_time_ref:
                #print(tf_name)
                df_tf = reindex_dataframe(df_tf, self.timestamp_ref,col_to_use_as_index='timestamp')
            df_tf.to_csv(path_to_save)
        
    
    def __str__(self):
        return str(self.tf_tree)
    
    def request_tf_a_in_frame_B(self,tfa,tfb,debug = True):
        """Compute the tf of the frame a in the frame b 

        Args:
            tfa (_type_): the name of the  frame a in the tf tree look in the folder tf utils to get the name
            tfb (_type_): the name of the  frame b in the tf tree look in the folder tf utils to get the name
            debug (bool, optional): _description_. Defaults to True.
        """
        using_ros_time = False
        linear_interpolation = False
        self.get_path_from_tf_a_to_b(tfa,tfb,debug=debug)
        
        if self.verify_if_tf_are_all_static():
            self.compute_tf_static()
        else:
            self.compute_tf(using_ros_time = using_ros_time,
                        linear_interpolation = linear_interpolation,
                        debug = debug)
        #self.save_tf(add_on="root_frame")
    

        
    def computed_tf_in_root_frame(self):
        """Compute all tf from the root frame
        """
        
        list_paths =  extract_paths(self.tf_tree)

        for i,path in enumerate(list_paths):
            if path[0] != self.tf_tree.root:
                list_paths.pop(i)

        tfa = self.tf_tree.root

        for path in tqdm(list_paths, desc="Computing transforms"):
            if len(path) == 1:
                continue
            tfb = path[0]
            tfa = path[-1]
            print("Computing tf from ", tfa, " in ", tfb)
            self.request_tf_a_in_frame_B(tfa, tfb, 
                        debug=False)
        self.save_tf()

if __name__ == "__main__":
    path_ = "/media/nicolassamson/ssd_NS/wilah/extracted_results/tf"
    
    query = Tfquery(path_)
    #query.computed_tf_in_root_frame()
    query.computed_tf_in_root_frame()
    #query.get_path_from_tf_a_to_b()
    #query.request_tf_a_in_frame_B("basemast","zedx_left_camera_optical_frame",debug=False)
    query.request_tf_a_in_frame_B("tong_left_tips","zedx_left_camera_optical_frame",debug=False)
    query.request_tf_a_in_frame_B("tong_right_tips","zedx_left_camera_optical_frame",debug=False)
    query.save_tf()

