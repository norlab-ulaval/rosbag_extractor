import math
import numpy as np
from pathlib import Path
from os.path import join
import pandas as pd

from rosbags.highlevel import AnyReader
from tqdm import tqdm
from treelib import Node, Tree
import yaml 
import pathlib
## NOTE: THIS ONLY EXTRACTS THE TF IN THE /TF message, NOT THE COVARIANCE NOR THE TWIST

    # extract_images_from_rosbag(bag_file, topic_name, output_folder, args,


class TreeNode:
    def __init__(self, name):
        self.name = name
        self.children = []


    def to_dict(self):
        """Converts the tree to a dictionary format for JSON export."""
        return {
            'name': self.name,
            'children': [child.to_dict() for child in self.children]
        }

    def to_dict(self):
        dico =  {} 

        level = []
        if self.children == []:

            
            return {self.name:[]}
        else:
            for tree_nodes in self.children:
                
                level.append(tree_nodes.to_dict())
            dico[self.name] = level
            
            return dico   
    def to_dict_2(self):
        dico =  {} 

        level = []
        if self.children == []:

            return self.name
        else:
            for tree_nodes in self.children:
                dico[tree_nodes.to_dict_2()] = self.name 
            
            return dico   

    def to_yaml(self,file_path):

        dico = self.to_dict_2()

        with open(file_path,"w") as file:
            yaml.safe_dump(dico,file)
        
        
def create_tree(node_dict):
    # Create a dictionary to store all nodes by name
    nodes = {}
    # Initialize tree nodes
    for child, parent in node_dict.items():
        if child not in nodes:
            nodes[child] = TreeNode(child)
        if parent not in nodes:
            nodes[parent] = TreeNode(parent)
    
    # Build the tree structure
    for child, parent in node_dict.items():
        nodes[parent].children.append(nodes[child])
    
    # Find the root (the node without a parent)
    # The root is the one that's not a child of any other node
    all_children = set(node_dict.keys())
    all_parents = set(node_dict.values())
    root_name = list(all_parents - all_children)[0]  # There should be only one root
    
    return nodes[root_name]

# Simple tree traversal to check the structure
def print_tree(node, level=0):
    print(' ' * level + node.name)
    for child in node.children:
        print_tree(child, level + 2)



def save_dict_to_yaml(dictionary, filename):
    with open(filename, 'w') as yaml_file:
        yaml.dump(dictionary, yaml_file, default_flow_style=False)  # default_flow_style=False makes it more readable


def extract_tf_from_rosbags(bag_file, topic_name, output_folder,args):

    odom_data = []
    tf_identification = True

    tf_tree = {}
    data_df = {}
    id_tf = 0 
    tree_test = Tree()
    tf_tree_folder = pathlib.Path(output_folder)/"tf_analysis"
    if tf_tree_folder.exists() == False:
        tf_tree_folder.mkdir()

    minimal_ros_time = -math.inf
    with AnyReader([Path(bag_file)]) as reader:
        # iterate over messages
        print(f"Extracting tf from topic \"{topic_name}\" to folder \"{output_folder.split('/')[-1]}\"")
        connections = [x for x in reader.connections if x.topic == topic_name]
        
        
        for connection, ros_time, rawdata in tqdm(reader.messages(connections=connections)):
            tf_msg = reader.deserialize(rawdata, connection.msgtype)
            
            # Extract the number of tf 
            #if tf_identification:
            list_tf = tf_msg.transforms
            nb_tf = len(list_tf)
            
            
            for i in range(nb_tf):
                parent_frame_id = list_tf[i].header.frame_id
                child_frame_id  = list_tf[i].child_frame_id
                
                if not tf_tree.get(child_frame_id,False):
                    data_df[child_frame_id] = []
                    tf_tree[child_frame_id] = parent_frame_id
                    
                    

                tf =list_tf[i]
                trans = tf.transform.translation
                rot = tf.transform.rotation
                tf_trans_np = [int(tf.header.stamp.sec * 1e9 + tf.header.stamp.nanosec),
                    ros_time, 
                    trans.x,
                    trans.y,
                    trans.z,
                    rot.x,
                    rot.y,
                    rot.z,
                    rot.w]
                data_df[child_frame_id].append(tf_trans_np)
        # Creates and save each dataframe
        for tf_id, data in data_df.items():
            data = pd.DataFrame(
                data,
                columns=[
                    "timestamp",
                    "ros_time",
                    "x",
                    "y",
                    "z",
                    "q_x",
                    "q_y",
                    "q_z",
                    "q_w"
                ],
            )
            path = join(output_folder,f"{tf_id}.csv")
            data.to_csv(path, index=False)
        # Extract the dictionnary

        #[print(f"{key}  {value}") for key, value in tf_tree.items()]
        
        save_dict_to_yaml(tf_tree, join(tf_tree_folder,f"{topic_name[1:]}_tree.yaml"))
        final_tree = tf_tree

        if args["linked_2_topic"] != []:
            
                
            result_folder = pathlib.Path(output_folder).parent
            
            
            
            

            for topic in args["linked_2_topic"]:
                analysis_folder = result_folder/topic[1:]/"tf_analysis"
                

                path_file = analysis_folder/f"{topic[1:]}_tree.yaml"
            
                with open(path_file, 'r') as yaml_file:
                    tree_2_ad = yaml.safe_load(yaml_file)  # default_flow_style=False makes it more readable
                    
                    final_tree.update(tree_2_ad)
                

            
        if args["last_tf_topic"]:    
            
            root = create_tree(final_tree)

            children = set(final_tree.keys())
            parents = set(final_tree.values())
            final_tree[(parents.difference(children)).pop()] = None 
            
            
            
            # extract the keys that are just parent
            #dico = root.to_dict()
            
            path_2_save = pathlib.Path(tf_tree_folder)/"combined_tf_tree.yaml"

            with open(path_2_save,"w") as file:
                yaml.safe_dump(final_tree,file)
                

            #root.to_yaml(path_2_save)
            
        


        
        


