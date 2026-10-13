//Maya ASCII 2018 scene
//Name: 01_vector_04_cross product.ma
//Last modified: Fri, Mar 25, 2022 11:40:30 AM
//Codeset: 1252
file -rdi 1 -ns "learning_vector_object" -rfn "learning_vector_objectRN" -op
		 "v=0;" -typ "mayaAscii" "C:/Users/Noman/Documents/maya/projects/default//assets/learning_vector_object.ma";
file -rdi 1 -ns "learning_vector_object1" -rfn "learning_vector_objectRN1" 
		-op "v=0;" -typ "mayaAscii" "C:/Users/Noman/Documents/maya/projects/default//assets/learning_vector_object.ma";
file -rdi 1 -ns "learning_vector_object2" -rfn "learning_vector_object1RN" 
		-typ "mayaAscii" "C:/Users/Noman/Documents/maya/projects/default//assets/learning_vector_object.ma";
file -rdi 1 -ns "learning_vector_object3" -rfn "learning_vector_object2RN" 
		-typ "mayaAscii" "C:/Users/Noman/Documents/maya/projects/default//assets/learning_vector_object.ma";
file -r -ns "learning_vector_object" -dr 1 -rfn "learning_vector_objectRN" -op "v=0;"
		 -typ "mayaAscii" "C:/Users/Noman/Documents/maya/projects/default//assets/learning_vector_object.ma";
file -r -ns "learning_vector_object1" -dr 1 -rfn "learning_vector_objectRN1" -op
		 "v=0;" -typ "mayaAscii" "C:/Users/Noman/Documents/maya/projects/default//assets/learning_vector_object.ma";
file -r -ns "learning_vector_object2" -dr 1 -rfn "learning_vector_object1RN" -typ
		 "mayaAscii" "C:/Users/Noman/Documents/maya/projects/default//assets/learning_vector_object.ma";
file -r -ns "learning_vector_object3" -dr 1 -rfn "learning_vector_object2RN" -typ
		 "mayaAscii" "C:/Users/Noman/Documents/maya/projects/default//assets/learning_vector_object.ma";
requires maya "2018";
requires "stereoCamera" "10.0";
requires "stereoCamera" "10.0";
currentUnit -l centimeter -a degree -t ntsc;
fileInfo "application" "maya";
fileInfo "product" "Maya 2018";
fileInfo "version" "2018";
fileInfo "cutIdentifier" "201706261615-f9658c4cfc";
fileInfo "osv" "Microsoft Windows 8 Business Edition, 64-bit  (Build 9200)\n";
createNode transform -s -n "persp";
	rename -uid "E36B79ED-40EC-7C3D-10BE-CAB521F7EE18";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 59.751780861960057 -0.91860201160750421 48.398537239625156 ;
	setAttr ".r" -type "double3" 5.6616472704010921 412.19999999997663 -6.4866170622965455e-16 ;
createNode camera -s -n "perspShape" -p "persp";
	rename -uid "32CF69C2-498C-F9DF-6E68-85A9142F6422";
	setAttr -k off ".v" no;
	setAttr ".fl" 34.999999999999993;
	setAttr ".coi" 76.24844686604159;
	setAttr ".imn" -type "string" "persp";
	setAttr ".den" -type "string" "persp_depth";
	setAttr ".man" -type "string" "persp_mask";
	setAttr ".tp" -type "double3" 5.0373355711898755 2.5411999849450009 4.4975753926688 ;
	setAttr ".hc" -type "string" "viewSet -p %camera";
createNode transform -s -n "top";
	rename -uid "2DC997DF-4CE5-1128-3F30-A2BE8239717E";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 0 1000.1 0 ;
	setAttr ".r" -type "double3" -89.999999999999986 0 0 ;
createNode camera -s -n "topShape" -p "top";
	rename -uid "17D89B90-46CE-B3CE-00D7-B6B62F3C7D92";
	setAttr -k off ".v" no;
	setAttr ".rnd" no;
	setAttr ".coi" 1000.1;
	setAttr ".ow" 30;
	setAttr ".imn" -type "string" "top";
	setAttr ".den" -type "string" "top_depth";
	setAttr ".man" -type "string" "top_mask";
	setAttr ".hc" -type "string" "viewSet -t %camera";
	setAttr ".o" yes;
createNode transform -s -n "front";
	rename -uid "BC11AF14-4C5F-0C81-DCF0-CDB72121E531";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 0 0 1000.1 ;
createNode camera -s -n "frontShape" -p "front";
	rename -uid "03EAE41A-4B21-3641-470B-8E848BF85CD4";
	setAttr -k off ".v" no;
	setAttr ".rnd" no;
	setAttr ".coi" 1000.1;
	setAttr ".ow" 30;
	setAttr ".imn" -type "string" "front";
	setAttr ".den" -type "string" "front_depth";
	setAttr ".man" -type "string" "front_mask";
	setAttr ".hc" -type "string" "viewSet -f %camera";
	setAttr ".o" yes;
createNode transform -s -n "side";
	rename -uid "499E71AA-4EEC-8343-1AB9-679F49EC3104";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 1000.1 0 0 ;
	setAttr ".r" -type "double3" 0 89.999999999999986 0 ;
createNode camera -s -n "sideShape" -p "side";
	rename -uid "F7FA1578-4866-C53A-1196-CEB45D55DD17";
	setAttr -k off ".v" no;
	setAttr ".rnd" no;
	setAttr ".coi" 1000.1;
	setAttr ".ow" 30;
	setAttr ".imn" -type "string" "side";
	setAttr ".den" -type "string" "side_depth";
	setAttr ".man" -type "string" "side_mask";
	setAttr ".hc" -type "string" "viewSet -s %camera";
	setAttr ".o" yes;
createNode transform -n "locator1";
	rename -uid "710F301C-425E-18B5-6F64-6D8AB3BA0C6D";
	setAttr ".t" -type "double3" -0.36421136097334639 9.1624509618721994 -0.050163335260734243 ;
createNode locator -n "locatorShape1" -p "locator1";
	rename -uid "D67CD08D-4EB5-C029-8D7A-DB9C31ED76CE";
	setAttr -k off ".v";
createNode transform -n "locator2";
	rename -uid "8CD05C7D-48C3-5D29-73E9-0FA12D4FD4A4";
	setAttr ".t" -type "double3" -2.3891807917085934 0.6021782224496306 9.7223428103356131 ;
createNode locator -n "locatorShape2" -p "locator2";
	rename -uid "0B0E4A2D-4610-B26B-7D19-C2A87B808976";
	setAttr -k off ".v";
createNode transform -n "locator3";
	rename -uid "9D28EF75-4D3F-213E-8798-94AF64F896B1";
	setAttr ".t" -type "double3" 12.779003551985207 2.212701907294349 -0.89345424542776186 ;
createNode locator -n "locatorShape3" -p "locator3";
	rename -uid "23DB0F8D-48C6-BC94-C67C-0D8531D432D4";
	setAttr -k off ".v";
createNode transform -n "pPlane1";
	rename -uid "1FA13B86-4DB9-A339-20D7-AAACB47F8277";
	setAttr ".t" -type "double3" 3.0982640540819339 -2.3524747636749304 0.25030346355783095 ;
createNode mesh -n "pPlaneShape1" -p "pPlane1";
	rename -uid "6534DDD9-4AB2-E402-3FE3-608666A6120C";
	setAttr -k off ".v";
	setAttr ".vir" yes;
	setAttr ".vif" yes;
	setAttr ".pv" -type "double2" 1 0 ;
	setAttr ".uvst[0].uvsn" -type "string" "map1";
	setAttr -s 4 ".uvst[0].uvsp[0:3]" -type "float2" 0 0 1 0 0 1 1 1;
	setAttr ".cuvs" -type "string" "map1";
	setAttr ".dcc" -type "string" "Ambient+Diffuse";
	setAttr ".covm[0]"  0 1 1;
	setAttr ".cdvm[0]"  0 1 1;
	setAttr -s 4 ".pt[0:3]" -type "float3"  -4.9874449 3.002986 8.9055147 
		7.1557703 -3.9950962 8.1287489 -2.9624753 11.540337 0.27773827 9.1807394 4.5397658 
		-0.56555271;
	setAttr -s 4 ".vt[0:3]"  -0.5 -1.110223e-16 0.5 0.5 -1.110223e-16 0.5
		 -0.5 1.110223e-16 -0.5 0.5 1.110223e-16 -0.5;
	setAttr -s 4 ".ed[0:3]"  0 1 0 0 2 0 1 3 0 2 3 0;
	setAttr -ch 4 ".fc[0]" -type "polyFaces" 
		f 4 0 2 -4 -2
		mu 0 4 0 1 3 2;
	setAttr ".cd" -type "dataPolyComponent" Index_Data Edge 0 ;
	setAttr ".cvd" -type "dataPolyComponent" Index_Data Vertex 0 ;
	setAttr ".pd[0]" -type "dataPolyComponent" Index_Data UV 0 ;
	setAttr ".hfd" -type "dataPolyComponent" Index_Data Face 0 ;
createNode transform -n "pCube1";
	rename -uid "B4CFEA48-4483-B103-1D2D-EC8398EAE3B8";
	setAttr ".t" -type "double3" -0.36421136097334639 9.1624509618721994 -0.050163335260734243 ;
	setAttr ".r" -type "double3" 41.215966596066124 8.8645046355454049 -23.28664081475802 ;
createNode mesh -n "pCubeShape1" -p "pCube1";
	rename -uid "82112FAC-493C-78F1-08B0-39B2D69C16FA";
	setAttr -k off ".v";
	setAttr ".vir" yes;
	setAttr ".vif" yes;
	setAttr ".pv" -type "double2" 0.5 0.125 ;
	setAttr ".uvst[0].uvsn" -type "string" "map1";
	setAttr -s 26 ".uvst[0].uvsp[0:25]" -type "float2" 0.375 0 0.625 0 0.375
		 0.25 0.625 0.25 0.375 0.5 0.625 0.5 0.375 0.75 0.625 0.75 0.375 1 0.625 1 0.875 0
		 0.875 0.25 0.125 0 0.125 0.25 0.375 0.25 0.625 0.25 0.625 0.5 0.375 0.5 0.375 0 0.625
		 0 0.625 0.25 0.375 0.25 0.625 0 0.875 0 0.875 0.25 0.625 0.25;
	setAttr ".cuvs" -type "string" "map1";
	setAttr ".dcc" -type "string" "Ambient+Diffuse";
	setAttr ".covm[0]"  0 1 1;
	setAttr ".cdvm[0]"  0 1 1;
	setAttr -s 12 ".pt[8:19]" -type "float3"  0 20.615602 0 0 20.615602 
		0 0 20.615602 0 0 20.615602 0 0 0 29.535173 0 0 29.535173 0 0 29.535173 0 0 29.535173 
		21.869541 0 0 21.869541 0 0 21.869541 0 0 21.869541 0 0;
	setAttr -s 20 ".vt[0:19]"  -0.5 -0.5 0.5 0.5 -0.5 0.5 -0.5 0.5 0.5 0.5 0.5 0.5
		 -0.5 0.5 -0.5 0.5 0.5 -0.5 -0.5 -0.5 -0.5 0.5 -0.5 -0.5 -0.5 1.5316447 0.5 0.5 1.5316447 0.5
		 0.5 1.5316447 -0.5 -0.5 1.5316447 -0.5 -0.5 -0.5 1.73345935 0.5 -0.5 1.73345935 0.5 0.5 1.73345935
		 -0.5 0.5 1.73345935 0.5 -0.5 -0.5 0.5 -0.5 0.5 0.5 0.5 -0.5 0.5 0.5 0.5;
	setAttr -s 36 ".ed[0:35]"  0 1 0 2 3 0 4 5 0 6 7 0 0 2 0 1 3 0 2 4 0
		 3 5 0 4 6 0 5 7 0 6 0 0 7 1 0 2 8 0 3 9 0 8 9 0 5 10 0 9 10 0 4 11 0 11 10 0 8 11 0
		 0 12 0 1 13 0 12 13 0 3 14 0 13 14 0 2 15 0 15 14 0 12 15 0 7 16 0 1 17 0 16 17 0
		 5 18 0 18 16 0 3 19 0 19 18 0 17 19 0;
	setAttr -s 18 -ch 72 ".fc[0:17]" -type "polyFaces" 
		f 4 22 24 -27 -28
		mu 0 4 18 19 20 21
		f 4 14 16 -19 -20
		mu 0 4 14 15 16 17
		f 4 2 9 -4 -9
		mu 0 4 4 5 7 6
		f 4 3 11 -1 -11
		mu 0 4 6 7 9 8
		f 4 -31 -33 -35 -36
		mu 0 4 22 23 24 25
		f 4 10 4 6 8
		mu 0 4 12 0 2 13
		f 4 1 13 -15 -13
		mu 0 4 2 3 15 14
		f 4 7 15 -17 -14
		mu 0 4 3 5 16 15
		f 4 -3 17 18 -16
		mu 0 4 5 4 17 16
		f 4 -7 12 19 -18
		mu 0 4 4 2 14 17
		f 4 0 21 -23 -21
		mu 0 4 0 1 19 18
		f 4 5 23 -25 -22
		mu 0 4 1 3 20 19
		f 4 -2 25 26 -24
		mu 0 4 3 2 21 20
		f 4 -5 20 27 -26
		mu 0 4 2 0 18 21
		f 4 -12 28 30 -30
		mu 0 4 1 10 23 22
		f 4 -10 31 32 -29
		mu 0 4 10 11 24 23
		f 4 -8 33 34 -32
		mu 0 4 11 3 25 24
		f 4 -6 29 35 -34
		mu 0 4 3 1 22 25;
	setAttr ".cd" -type "dataPolyComponent" Index_Data Edge 0 ;
	setAttr ".cvd" -type "dataPolyComponent" Index_Data Vertex 0 ;
	setAttr ".pd[0]" -type "dataPolyComponent" Index_Data UV 0 ;
	setAttr ".hfd" -type "dataPolyComponent" Index_Data Face 0 ;
createNode lightLinker -s -n "lightLinker1";
	rename -uid "D58229CD-4CAB-E4F4-90F0-C1B69E3051C7";
	setAttr -s 18 ".lnk";
	setAttr -s 18 ".slnk";
createNode shapeEditorManager -n "shapeEditorManager";
	rename -uid "20634E33-4F3F-FADD-58C7-1D9E20A8DB62";
createNode poseInterpolatorManager -n "poseInterpolatorManager";
	rename -uid "AFD7593A-4D25-CC31-D5DF-3C8142A67D7D";
createNode displayLayerManager -n "layerManager";
	rename -uid "1D4C5689-4DAB-B3B8-CEA2-FD9528DAF363";
createNode displayLayer -n "defaultLayer";
	rename -uid "DC5AFEF8-4743-69A9-7080-B898306CA3DE";
createNode renderLayerManager -n "renderLayerManager";
	rename -uid "6AE15E12-4BF7-6FB7-C8C1-A8A887245C0B";
createNode renderLayer -n "defaultRenderLayer";
	rename -uid "E3E283A0-414C-5D1F-ED43-41A67FD6660D";
	setAttr ".g" yes;
createNode plusMinusAverage -n "vec_A";
	rename -uid "BF5E7007-44E9-9D88-A7B3-8CBABDD5E7EF";
	setAttr ".op" 2;
	setAttr -s 2 ".i3";
	setAttr -s 2 ".i3";
createNode plusMinusAverage -n "vec_B";
	rename -uid "6D6DE9A1-4760-709E-F9C1-08AEC3AAD9A7";
	setAttr ".op" 2;
	setAttr -s 2 ".i3";
	setAttr -s 2 ".i3";
createNode reference -n "learning_vector_objectRN";
	rename -uid "8BB3149F-4EE7-DD1F-29EA-059EBA4641C9";
	setAttr ".ed" -type "dataReferenceEdits" 
		"learning_vector_objectRN"
		"learning_vector_objectRN" 0
		"learning_vector_objectRN" 4
		2 "|learning_vector_object:vector_grp|learning_vector_object:headZro_grp|learning_vector_object:headOffset_grp|learning_vector_object:head_ctrl" 
		"translate" " -type \"double3\" -2.38918079170859343 0.6021782224496306 9.72234281033561309"
		
		2 "|learning_vector_object:vector_grp|learning_vector_object:headZro_grp|learning_vector_object:headOffset_grp|learning_vector_object:head_ctrl" 
		"color" " -k 1 0"
		2 "|learning_vector_object:vector_grp|learning_vector_object:headZro_grp|learning_vector_object:headOffset_grp|learning_vector_object:head_ctrl|learning_vector_object:annotationLocator1|learning_vector_object:annotation1|learning_vector_object:annotationShape1" 
		"text" " -type \"string\" \"vector_A\""
		2 "|learning_vector_object:vector_grp|learning_vector_object:tailZro_grp|learning_vector_object:tailOffset_grp|learning_vector_object:tail_ctrl" 
		"translate" " -type \"double3\" -0.36421136097334639 9.16245096187219943 -0.050163335260734243";
	setAttr ".ptag" -type "string" "";
lockNode -l 1 ;
createNode reference -n "learning_vector_objectRN1";
	rename -uid "F4DC52A5-49B1-8544-BFB7-AB8D4EC67EF3";
	setAttr ".phl[1]" 0;
	setAttr ".ed" -type "dataReferenceEdits" 
		"learning_vector_objectRN1"
		"learning_vector_objectRN1" 0
		"learning_vector_objectRN1" 4
		2 "|learning_vector_object1:vector_grp" "visibility" " 0"
		2 "|learning_vector_object1:vector_grp|learning_vector_object1:headZro_grp|learning_vector_object1:headOffset_grp|learning_vector_object1:head_ctrl|learning_vector_object1:annotationLocator1|learning_vector_object1:annotation1|learning_vector_object1:annotationShape1" 
		"text" " -type \"string\" \"vector_B\""
		2 "|learning_vector_object1:vector_grp|learning_vector_object1:tailZro_grp|learning_vector_object1:tailOffset_grp|learning_vector_object1:tail_ctrl" 
		"translate" " -type \"double3\" -0.36421136097334639 9.16245096187219943 -0.050163335260734243"
		
		5 4 "learning_vector_objectRN1" "|learning_vector_object1:vector_grp|learning_vector_object1:headZro_grp|learning_vector_object1:headOffset_grp|learning_vector_object1:head_ctrl.translate" 
		"learning_vector_objectRN1.placeHolderList[1]" "";
	setAttr ".ptag" -type "string" "";
lockNode -l 1 ;
createNode vectorProduct -n "vec_C";
	rename -uid "54D92C55-47DD-9B48-FBE5-F69189D47723";
	setAttr ".op" 2;
createNode reference -n "sharedReferenceNode";
	rename -uid "B4CE3F4F-43EF-1C7A-862E-828A3A70CE63";
	setAttr ".ed" -type "dataReferenceEdits" 
		"sharedReferenceNode";
createNode reference -n "learning_vector_object1RN";
	rename -uid "8DE191CF-4843-06D4-2EB7-21A9A714227E";
	setAttr -s 5 ".phl";
	setAttr ".phl[1]" 0;
	setAttr ".phl[2]" 0;
	setAttr ".phl[3]" 0;
	setAttr ".phl[4]" 0;
	setAttr ".phl[5]" 0;
	setAttr ".ed" -type "dataReferenceEdits" 
		"learning_vector_object1RN"
		"learning_vector_object1RN" 0
		"learning_vector_object1RN" 6
		2 "|learning_vector_object2:vector_grp|learning_vector_object2:headZro_grp|learning_vector_object2:headOffset_grp|learning_vector_object2:head_ctrl|learning_vector_object2:annotationLocator1|learning_vector_object2:annotation1|learning_vector_object2:annotationShape1" 
		"text" " -type \"string\" \"vector_C\""
		5 4 "learning_vector_object1RN" "|learning_vector_object2:vector_grp.translate" 
		"learning_vector_object1RN.placeHolderList[1]" ""
		5 4 "learning_vector_object1RN" "|learning_vector_object2:vector_grp|learning_vector_object2:headZro_grp|learning_vector_object2:headOffset_grp|learning_vector_object2:head_ctrl.translate" 
		"learning_vector_object1RN.placeHolderList[2]" ""
		5 3 "learning_vector_object1RN" "|learning_vector_object2:vector_grp|learning_vector_object2:headZro_grp|learning_vector_object2:headOffset_grp|learning_vector_object2:head_ctrl.message" 
		"learning_vector_object1RN.placeHolderList[3]" ""
		5 3 "learning_vector_object1RN" "|learning_vector_object2:vector_grp|learning_vector_object2:headZro_grp|learning_vector_object2:headOffset_grp|learning_vector_object2:head_ctrl|learning_vector_object2:head_ctrlShape.message" 
		"learning_vector_object1RN.placeHolderList[4]" ""
		5 3 "learning_vector_object1RN" "learning_vector_object2:vector_head.message" 
		"learning_vector_object1RN.placeHolderList[5]" "";
lockNode -l 1 ;
createNode script -n "sceneConfigurationScriptNode";
	rename -uid "55F93E22-4161-911C-A805-D9BF763565D4";
	setAttr ".b" -type "string" "playbackOptions -min 1 -max 120 -ast 1 -aet 200 ";
	setAttr ".st" 6;
createNode vectorProduct -n "vec_D";
	rename -uid "5D1DA7F1-4DE0-08F5-FF0D-7DA565191B63";
	setAttr ".op" 2;
createNode reference -n "learning_vector_object2RN";
	rename -uid "994CD58C-422E-3A21-7073-9A886CE15E7F";
	setAttr -s 68 ".phl";
	setAttr ".phl[1]" 0;
	setAttr ".phl[2]" 0;
	setAttr ".phl[3]" 0;
	setAttr ".phl[4]" 0;
	setAttr ".phl[5]" 0;
	setAttr ".phl[6]" 0;
	setAttr ".phl[7]" 0;
	setAttr ".phl[8]" 0;
	setAttr ".phl[9]" 0;
	setAttr ".phl[10]" 0;
	setAttr ".phl[11]" 0;
	setAttr ".phl[12]" 0;
	setAttr ".phl[13]" 0;
	setAttr ".phl[14]" 0;
	setAttr ".phl[15]" 0;
	setAttr ".phl[16]" 0;
	setAttr ".phl[17]" 0;
	setAttr ".phl[18]" 0;
	setAttr ".phl[19]" 0;
	setAttr ".phl[20]" 0;
	setAttr ".phl[21]" 0;
	setAttr ".phl[22]" 0;
	setAttr ".phl[23]" 0;
	setAttr ".phl[24]" 0;
	setAttr ".phl[25]" 0;
	setAttr ".phl[26]" 0;
	setAttr ".phl[27]" 0;
	setAttr ".phl[28]" 0;
	setAttr ".phl[29]" 0;
	setAttr ".phl[30]" 0;
	setAttr ".phl[31]" 0;
	setAttr ".phl[32]" 0;
	setAttr ".phl[33]" 0;
	setAttr ".phl[34]" 0;
	setAttr ".phl[35]" 0;
	setAttr ".phl[36]" 0;
	setAttr ".phl[37]" 0;
	setAttr ".phl[38]" 0;
	setAttr ".phl[39]" 0;
	setAttr ".phl[40]" 0;
	setAttr ".phl[41]" 0;
	setAttr ".phl[42]" 0;
	setAttr ".phl[43]" 0;
	setAttr ".phl[44]" 0;
	setAttr ".phl[45]" 0;
	setAttr ".phl[46]" 0;
	setAttr ".phl[47]" 0;
	setAttr ".phl[48]" 0;
	setAttr ".phl[49]" 0;
	setAttr ".phl[50]" 0;
	setAttr ".phl[51]" 0;
	setAttr ".phl[52]" 0;
	setAttr ".phl[53]" 0;
	setAttr ".phl[54]" 0;
	setAttr ".phl[55]" 0;
	setAttr ".phl[56]" 0;
	setAttr ".phl[57]" 0;
	setAttr ".phl[58]" 0;
	setAttr ".phl[59]" 0;
	setAttr ".phl[60]" 0;
	setAttr ".phl[61]" 0;
	setAttr ".phl[62]" 0;
	setAttr ".phl[63]" 0;
	setAttr ".phl[64]" 0;
	setAttr ".phl[65]" 0;
	setAttr ".phl[66]" 0;
	setAttr ".phl[67]" 0;
	setAttr ".phl[68]" 0;
	setAttr ".ed" -type "dataReferenceEdits" 
		"learning_vector_object2RN"
		"learning_vector_object2RN" 0
		"learning_vector_object2RN" 70
		2 "|learning_vector_object3:vector_grp" "translate" " -type \"double3\" -0.36421136097334639 9.16245096187219943 -0.050163335260734243"
		
		2 "|learning_vector_object3:vector_grp|learning_vector_object3:headZro_grp|learning_vector_object3:headOffset_grp|learning_vector_object3:head_ctrl|learning_vector_object3:annotationLocator1|learning_vector_object3:annotation1|learning_vector_object3:annotationShape1" 
		"text" " -type \"string\" \"vector_D\""
		5 3 "learning_vector_object2RN" "|learning_vector_object3:vector_grp.message" 
		"learning_vector_object2RN.placeHolderList[1]" ""
		5 3 "learning_vector_object2RN" "|learning_vector_object3:vector_grp|learning_vector_object3:jnt_grp.message" 
		"learning_vector_object2RN.placeHolderList[2]" ""
		5 3 "learning_vector_object2RN" "|learning_vector_object3:vector_grp|learning_vector_object3:jnt_grp|learning_vector_object3:tail.message" 
		"learning_vector_object2RN.placeHolderList[3]" ""
		5 3 "learning_vector_object2RN" "|learning_vector_object3:vector_grp|learning_vector_object3:jnt_grp|learning_vector_object3:tail|learning_vector_object3:tail_parCons.message" 
		"learning_vector_object2RN.placeHolderList[4]" ""
		5 3 "learning_vector_object2RN" "|learning_vector_object3:vector_grp|learning_vector_object3:jnt_grp|learning_vector_object3:tail|learning_vector_object3:tail_scalCons.message" 
		"learning_vector_object2RN.placeHolderList[5]" ""
		5 3 "learning_vector_object2RN" "|learning_vector_object3:vector_grp|learning_vector_object3:jnt_grp|learning_vector_object3:head.message" 
		"learning_vector_object2RN.placeHolderList[6]" ""
		5 3 "learning_vector_object2RN" "|learning_vector_object3:vector_grp|learning_vector_object3:jnt_grp|learning_vector_object3:head|learning_vector_object3:head_parCons.message" 
		"learning_vector_object2RN.placeHolderList[7]" ""
		5 3 "learning_vector_object2RN" "|learning_vector_object3:vector_grp|learning_vector_object3:jnt_grp|learning_vector_object3:head|learning_vector_object3:head_scalCons.message" 
		"learning_vector_object2RN.placeHolderList[8]" ""
		5 3 "learning_vector_object2RN" "|learning_vector_object3:vector_grp|learning_vector_object3:headZro_grp.message" 
		"learning_vector_object2RN.placeHolderList[9]" ""
		5 3 "learning_vector_object2RN" "|learning_vector_object3:vector_grp|learning_vector_object3:headZro_grp|learning_vector_object3:headOffset_grp.message" 
		"learning_vector_object2RN.placeHolderList[10]" ""
		5 4 "learning_vector_object2RN" "|learning_vector_object3:vector_grp|learning_vector_object3:headZro_grp|learning_vector_object3:headOffset_grp|learning_vector_object3:head_ctrl.translate" 
		"learning_vector_object2RN.placeHolderList[11]" ""
		5 3 "learning_vector_object2RN" "|learning_vector_object3:vector_grp|learning_vector_object3:headZro_grp|learning_vector_object3:headOffset_grp|learning_vector_object3:head_ctrl.message" 
		"learning_vector_object2RN.placeHolderList[12]" ""
		5 3 "learning_vector_object2RN" "|learning_vector_object3:vector_grp|learning_vector_object3:headZro_grp|learning_vector_object3:headOffset_grp|learning_vector_object3:head_ctrl|learning_vector_object3:head_ctrlShape.message" 
		"learning_vector_object2RN.placeHolderList[13]" ""
		5 3 "learning_vector_object2RN" "|learning_vector_object3:vector_grp|learning_vector_object3:headZro_grp|learning_vector_object3:headOffset_grp|learning_vector_object3:head_ctrl|learning_vector_object3:head_gmbCtrl.message" 
		"learning_vector_object2RN.placeHolderList[14]" ""
		5 3 "learning_vector_object2RN" "|learning_vector_object3:vector_grp|learning_vector_object3:headZro_grp|learning_vector_object3:headOffset_grp|learning_vector_object3:head_ctrl|learning_vector_object3:head_gmbCtrl|learning_vector_object3:head_gmbCtrlShape.message" 
		"learning_vector_object2RN.placeHolderList[15]" ""
		5 3 "learning_vector_object2RN" "|learning_vector_object3:vector_grp|learning_vector_object3:headZro_grp|learning_vector_object3:headOffset_grp|learning_vector_object3:head_ctrl|learning_vector_object3:annotationLocator1.message" 
		"learning_vector_object2RN.placeHolderList[16]" ""
		5 3 "learning_vector_object2RN" "|learning_vector_object3:vector_grp|learning_vector_object3:headZro_grp|learning_vector_object3:headOffset_grp|learning_vector_object3:head_ctrl|learning_vector_object3:annotationLocator1|learning_vector_object3:annotationLocator1Shape.message" 
		"learning_vector_object2RN.placeHolderList[17]" ""
		5 3 "learning_vector_object2RN" "|learning_vector_object3:vector_grp|learning_vector_object3:headZro_grp|learning_vector_object3:headOffset_grp|learning_vector_object3:head_ctrl|learning_vector_object3:annotationLocator1|learning_vector_object3:annotation1.message" 
		"learning_vector_object2RN.placeHolderList[18]" ""
		5 3 "learning_vector_object2RN" "|learning_vector_object3:vector_grp|learning_vector_object3:headZro_grp|learning_vector_object3:headOffset_grp|learning_vector_object3:head_ctrl|learning_vector_object3:annotationLocator1|learning_vector_object3:annotation1|learning_vector_object3:annotationShape1.message" 
		"learning_vector_object2RN.placeHolderList[19]" ""
		5 3 "learning_vector_object2RN" "|learning_vector_object3:vector_grp|learning_vector_object3:tailZro_grp.message" 
		"learning_vector_object2RN.placeHolderList[20]" ""
		5 3 "learning_vector_object2RN" "|learning_vector_object3:vector_grp|learning_vector_object3:tailZro_grp|learning_vector_object3:tailOffset_grp.message" 
		"learning_vector_object2RN.placeHolderList[21]" ""
		5 3 "learning_vector_object2RN" "|learning_vector_object3:vector_grp|learning_vector_object3:tailZro_grp|learning_vector_object3:tailOffset_grp|learning_vector_object3:tail_ctrl.message" 
		"learning_vector_object2RN.placeHolderList[22]" ""
		5 3 "learning_vector_object2RN" "|learning_vector_object3:vector_grp|learning_vector_object3:tailZro_grp|learning_vector_object3:tailOffset_grp|learning_vector_object3:tail_ctrl|learning_vector_object3:tail_ctrlShape.message" 
		"learning_vector_object2RN.placeHolderList[23]" ""
		5 3 "learning_vector_object2RN" "|learning_vector_object3:vector_grp|learning_vector_object3:tailZro_grp|learning_vector_object3:tailOffset_grp|learning_vector_object3:tail_ctrl|learning_vector_object3:tail_gmbCtrl.message" 
		"learning_vector_object2RN.placeHolderList[24]" ""
		5 3 "learning_vector_object2RN" "|learning_vector_object3:vector_grp|learning_vector_object3:tailZro_grp|learning_vector_object3:tailOffset_grp|learning_vector_object3:tail_ctrl|learning_vector_object3:tail_gmbCtrl|learning_vector_object3:tail_gmbCtrlShape.message" 
		"learning_vector_object2RN.placeHolderList[25]" ""
		5 3 "learning_vector_object2RN" "|learning_vector_object3:vector_grp|learning_vector_object3:geo_grp.message" 
		"learning_vector_object2RN.placeHolderList[26]" ""
		5 3 "learning_vector_object2RN" "|learning_vector_object3:vector_grp|learning_vector_object3:geo_grp|learning_vector_object3:vector_yellow_ply.message" 
		"learning_vector_object2RN.placeHolderList[27]" ""
		5 3 "learning_vector_object2RN" "|learning_vector_object3:vector_grp|learning_vector_object3:geo_grp|learning_vector_object3:vector_yellow_ply|learning_vector_object3:vector_yellow_plyShape.message" 
		"learning_vector_object2RN.placeHolderList[28]" ""
		5 3 "learning_vector_object2RN" "|learning_vector_object3:vector_grp|learning_vector_object3:geo_grp|learning_vector_object3:vector_yellow_ply|learning_vector_object3:vector_yellow_plyShapeOrig.message" 
		"learning_vector_object2RN.placeHolderList[29]" ""
		5 3 "learning_vector_object2RN" "|learning_vector_object3:vector_grp|learning_vector_object3:geo_grp|learning_vector_object3:vector_blue_ply.message" 
		"learning_vector_object2RN.placeHolderList[30]" ""
		5 3 "learning_vector_object2RN" "|learning_vector_object3:vector_grp|learning_vector_object3:geo_grp|learning_vector_object3:vector_blue_ply|learning_vector_object3:vector_blue_plyShape.message" 
		"learning_vector_object2RN.placeHolderList[31]" ""
		5 3 "learning_vector_object2RN" "|learning_vector_object3:vector_grp|learning_vector_object3:geo_grp|learning_vector_object3:vector_blue_ply|learning_vector_object3:vector_blue_plyShapeOrig.message" 
		"learning_vector_object2RN.placeHolderList[32]" ""
		5 3 "learning_vector_object2RN" "|learning_vector_object3:vector_grp|learning_vector_object3:geo_grp|learning_vector_object3:vector_blue_ply|learning_vector_object3:vector_blue_plyShapeOrig1.message" 
		"learning_vector_object2RN.placeHolderList[33]" ""
		5 3 "learning_vector_object2RN" "|learning_vector_object3:vector_grp|learning_vector_object3:geo_grp|learning_vector_object3:vector_red_ply.message" 
		"learning_vector_object2RN.placeHolderList[34]" ""
		5 3 "learning_vector_object2RN" "|learning_vector_object3:vector_grp|learning_vector_object3:geo_grp|learning_vector_object3:vector_red_ply|learning_vector_object3:vector_red_plyShape.message" 
		"learning_vector_object2RN.placeHolderList[35]" ""
		5 3 "learning_vector_object2RN" "|learning_vector_object3:vector_grp|learning_vector_object3:geo_grp|learning_vector_object3:vector_red_ply|learning_vector_object3:vector_red_plyShapeOrig.message" 
		"learning_vector_object2RN.placeHolderList[36]" ""
		5 3 "learning_vector_object2RN" "|learning_vector_object3:vector_grp|learning_vector_object3:geo_grp|learning_vector_object3:vector_red_ply|learning_vector_object3:vector_red_plyShapeOrig1.message" 
		"learning_vector_object2RN.placeHolderList[37]" ""
		5 3 "learning_vector_object2RN" "learning_vector_object3:shapeEditorManager.message" 
		"learning_vector_object2RN.placeHolderList[38]" ""
		5 3 "learning_vector_object2RN" "learning_vector_object3:poseInterpolatorManager.message" 
		"learning_vector_object2RN.placeHolderList[39]" ""
		5 3 "learning_vector_object2RN" "learning_vector_object3:layerManager.message" 
		"learning_vector_object2RN.placeHolderList[40]" ""
		5 3 "learning_vector_object2RN" "learning_vector_object3:defaultLayer.message" 
		"learning_vector_object2RN.placeHolderList[41]" ""
		5 3 "learning_vector_object2RN" "learning_vector_object3:defaultRenderLayer.message" 
		"learning_vector_object2RN.placeHolderList[42]" ""
		5 3 "learning_vector_object2RN" "learning_vector_object3:sceneConfigurationScriptNode.message" 
		"learning_vector_object2RN.placeHolderList[43]" ""
		5 3 "learning_vector_object2RN" "learning_vector_object3:rampShader1.message" 
		"learning_vector_object2RN.placeHolderList[44]" ""
		5 3 "learning_vector_object2RN" "learning_vector_object3:rampShader1SG.message" 
		"learning_vector_object2RN.placeHolderList[45]" ""
		5 3 "learning_vector_object2RN" "learning_vector_object3:yellow_mat.message" 
		"learning_vector_object2RN.placeHolderList[46]" ""
		5 3 "learning_vector_object2RN" "learning_vector_object3:surfaceShader1SG.message" 
		"learning_vector_object2RN.placeHolderList[47]" ""
		5 3 "learning_vector_object2RN" "learning_vector_object3:vector_head.message" 
		"learning_vector_object2RN.placeHolderList[48]" ""
		5 3 "learning_vector_object2RN" "learning_vector_object3:bindPose2.message" 
		"learning_vector_object2RN.placeHolderList[49]" ""
		5 3 "learning_vector_object2RN" "learning_vector_object3:skinCluster1.message" 
		"learning_vector_object2RN.placeHolderList[50]" ""
		5 3 "learning_vector_object2RN" "learning_vector_object3:skinCluster1Set.message" 
		"learning_vector_object2RN.placeHolderList[51]" ""
		5 3 "learning_vector_object2RN" "learning_vector_object3:tweak1.message" 
		"learning_vector_object2RN.placeHolderList[52]" ""
		5 3 "learning_vector_object2RN" "learning_vector_object3:tweakSet1.message" 
		"learning_vector_object2RN.placeHolderList[53]" ""
		5 3 "learning_vector_object2RN" "learning_vector_object3:surfaceShader2.message" 
		"learning_vector_object2RN.placeHolderList[54]" ""
		5 3 "learning_vector_object2RN" "learning_vector_object3:surfaceShader2SG.message" 
		"learning_vector_object2RN.placeHolderList[55]" ""
		5 3 "learning_vector_object2RN" "learning_vector_object3:surfaceShader3.message" 
		"learning_vector_object2RN.placeHolderList[56]" ""
		5 3 "learning_vector_object2RN" "learning_vector_object3:surfaceShader3SG.message" 
		"learning_vector_object2RN.placeHolderList[57]" ""
		5 3 "learning_vector_object2RN" "learning_vector_object3:yellow_cnd.message" 
		"learning_vector_object2RN.placeHolderList[58]" ""
		5 3 "learning_vector_object2RN" "learning_vector_object3:blue_cnd.message" 
		"learning_vector_object2RN.placeHolderList[59]" ""
		5 3 "learning_vector_object2RN" "learning_vector_object3:red_cnd.message" 
		"learning_vector_object2RN.placeHolderList[60]" ""
		5 3 "learning_vector_object2RN" "learning_vector_object3:skinCluster2.message" 
		"learning_vector_object2RN.placeHolderList[61]" ""
		5 3 "learning_vector_object2RN" "learning_vector_object3:tweak2.message" 
		"learning_vector_object2RN.placeHolderList[62]" ""
		5 3 "learning_vector_object2RN" "learning_vector_object3:skinCluster2Set.message" 
		"learning_vector_object2RN.placeHolderList[63]" ""
		5 3 "learning_vector_object2RN" "learning_vector_object3:tweakSet2.message" 
		"learning_vector_object2RN.placeHolderList[64]" ""
		5 3 "learning_vector_object2RN" "learning_vector_object3:skinCluster3.message" 
		"learning_vector_object2RN.placeHolderList[65]" ""
		5 3 "learning_vector_object2RN" "learning_vector_object3:tweak3.message" 
		"learning_vector_object2RN.placeHolderList[66]" ""
		5 3 "learning_vector_object2RN" "learning_vector_object3:skinCluster3Set.message" 
		"learning_vector_object2RN.placeHolderList[67]" ""
		5 3 "learning_vector_object2RN" "learning_vector_object3:tweakSet3.message" 
		"learning_vector_object2RN.placeHolderList[68]" "";
lockNode -l 1 ;
createNode nodeGraphEditorInfo -n "MayaNodeEditorSavedTabsInfo";
	rename -uid "50462B61-40E5-FFE1-4987-528E6F3F7CAD";
	setAttr ".tgi[0].tn" -type "string" "Untitled_1";
	setAttr ".tgi[0].vl" -type "double2" -220.59776225753566 -622.61902287839064 ;
	setAttr ".tgi[0].vh" -type "double2" 2292.0262513749344 617.85711830570699 ;
	setAttr -s 78 ".tgi[0].ni";
	setAttr ".tgi[0].ni[0].x" -105.71428680419922;
	setAttr ".tgi[0].ni[0].y" 281.42855834960938;
	setAttr ".tgi[0].ni[0].nvs" 18306;
	setAttr ".tgi[0].ni[1].x" 1702.857177734375;
	setAttr ".tgi[0].ni[1].y" -1668.5714111328125;
	setAttr ".tgi[0].ni[1].nvs" 18304;
	setAttr ".tgi[0].ni[2].x" 1737.142822265625;
	setAttr ".tgi[0].ni[2].y" 98.571426391601563;
	setAttr ".tgi[0].ni[2].nvs" 18304;
	setAttr ".tgi[0].ni[3].x" 1702.857177734375;
	setAttr ".tgi[0].ni[3].y" -1365.7142333984375;
	setAttr ".tgi[0].ni[3].nvs" 18304;
	setAttr ".tgi[0].ni[4].x" 815.71429443359375;
	setAttr ".tgi[0].ni[4].y" 142.85714721679688;
	setAttr ".tgi[0].ni[4].nvs" 1923;
	setAttr ".tgi[0].ni[5].x" -140;
	setAttr ".tgi[0].ni[5].y" 2010;
	setAttr ".tgi[0].ni[5].nvs" 18304;
	setAttr ".tgi[0].ni[6].x" 1702.857177734375;
	setAttr ".tgi[0].ni[6].y" -608.5714111328125;
	setAttr ".tgi[0].ni[6].nvs" 18304;
	setAttr ".tgi[0].ni[7].x" 1702.857177734375;
	setAttr ".tgi[0].ni[7].y" 602.85711669921875;
	setAttr ".tgi[0].ni[7].nvs" 18304;
	setAttr ".tgi[0].ni[8].x" 167.14285278320313;
	setAttr ".tgi[0].ni[8].y" 2098.571533203125;
	setAttr ".tgi[0].ni[8].nvs" 18304;
	setAttr ".tgi[0].ni[9].x" -412.85714721679688;
	setAttr ".tgi[0].ni[9].y" -194.28572082519531;
	setAttr ".tgi[0].ni[9].nvs" 1923;
	setAttr ".tgi[0].ni[10].x" -754.28570556640625;
	setAttr ".tgi[0].ni[10].y" 1884.2857666015625;
	setAttr ".tgi[0].ni[10].nvs" 18304;
	setAttr ".tgi[0].ni[11].x" 1702.857177734375;
	setAttr ".tgi[0].ni[11].y" -1214.2857666015625;
	setAttr ".tgi[0].ni[11].nvs" 18304;
	setAttr ".tgi[0].ni[12].x" 781.4285888671875;
	setAttr ".tgi[0].ni[12].y" 2050;
	setAttr ".tgi[0].ni[12].nvs" 18304;
	setAttr ".tgi[0].ni[13].x" -140;
	setAttr ".tgi[0].ni[13].y" 2132.857177734375;
	setAttr ".tgi[0].ni[13].nvs" 18304;
	setAttr ".tgi[0].ni[14].x" 1395.7142333984375;
	setAttr ".tgi[0].ni[14].y" 1872.857177734375;
	setAttr ".tgi[0].ni[14].nvs" 18304;
	setAttr ".tgi[0].ni[15].x" 781.4285888671875;
	setAttr ".tgi[0].ni[15].y" 1510;
	setAttr ".tgi[0].ni[15].nvs" 18304;
	setAttr ".tgi[0].ni[16].x" -754.28570556640625;
	setAttr ".tgi[0].ni[16].y" 1761.4285888671875;
	setAttr ".tgi[0].ni[16].nvs" 18304;
	setAttr ".tgi[0].ni[17].x" 1430;
	setAttr ".tgi[0].ni[17].y" -24.285715103149414;
	setAttr ".tgi[0].ni[17].nvs" 18304;
	setAttr ".tgi[0].ni[18].x" -140;
	setAttr ".tgi[0].ni[18].y" 1887.142822265625;
	setAttr ".tgi[0].ni[18].nvs" 18304;
	setAttr ".tgi[0].ni[19].x" 474.28570556640625;
	setAttr ".tgi[0].ni[19].y" 2272.857177734375;
	setAttr ".tgi[0].ni[19].nvs" 18304;
	setAttr ".tgi[0].ni[20].x" 1702.857177734375;
	setAttr ".tgi[0].ni[20].y" -760;
	setAttr ".tgi[0].ni[20].nvs" 18304;
	setAttr ".tgi[0].ni[21].x" 1702.857177734375;
	setAttr ".tgi[0].ni[21].y" -1820;
	setAttr ".tgi[0].ni[21].nvs" 18304;
	setAttr ".tgi[0].ni[22].x" 1702.857177734375;
	setAttr ".tgi[0].ni[22].y" -2425.71435546875;
	setAttr ".tgi[0].ni[22].nvs" 18304;
	setAttr ".tgi[0].ni[23].x" 201.42857360839844;
	setAttr ".tgi[0].ni[23].y" 147.14285278320313;
	setAttr ".tgi[0].ni[23].nvs" 18306;
	setAttr ".tgi[0].ni[24].x" 1702.857177734375;
	setAttr ".tgi[0].ni[24].y" 148.57142639160156;
	setAttr ".tgi[0].ni[24].nvs" 18304;
	setAttr ".tgi[0].ni[25].x" 1395.7142333984375;
	setAttr ".tgi[0].ni[25].y" 1272.857177734375;
	setAttr ".tgi[0].ni[25].nvs" 18304;
	setAttr ".tgi[0].ni[26].x" 531.00555419921875;
	setAttr ".tgi[0].ni[26].y" 380.99795532226563;
	setAttr ".tgi[0].ni[26].nvs" 18306;
	setAttr ".tgi[0].ni[27].x" 1702.857177734375;
	setAttr ".tgi[0].ni[27].y" -911.4285888671875;
	setAttr ".tgi[0].ni[27].nvs" 18304;
	setAttr ".tgi[0].ni[28].x" 1395.7142333984375;
	setAttr ".tgi[0].ni[28].y" 1570;
	setAttr ".tgi[0].ni[28].nvs" 18304;
	setAttr ".tgi[0].ni[29].x" 1702.857177734375;
	setAttr ".tgi[0].ni[29].y" -2122.857177734375;
	setAttr ".tgi[0].ni[29].nvs" 18304;
	setAttr ".tgi[0].ni[30].x" 1737.142822265625;
	setAttr ".tgi[0].ni[30].y" -147.14285278320313;
	setAttr ".tgi[0].ni[30].nvs" 18304;
	setAttr ".tgi[0].ni[31].x" 1395.7142333984375;
	setAttr ".tgi[0].ni[31].y" 451.42855834960938;
	setAttr ".tgi[0].ni[31].nvs" 18304;
	setAttr ".tgi[0].ni[32].x" 1702.857177734375;
	setAttr ".tgi[0].ni[32].y" -154.28572082519531;
	setAttr ".tgi[0].ni[32].nvs" 18304;
	setAttr ".tgi[0].ni[33].x" 1702.857177734375;
	setAttr ".tgi[0].ni[33].y" 1750;
	setAttr ".tgi[0].ni[33].nvs" 18304;
	setAttr ".tgi[0].ni[34].x" 1395.7142333984375;
	setAttr ".tgi[0].ni[34].y" 1750;
	setAttr ".tgi[0].ni[34].nvs" 18304;
	setAttr ".tgi[0].ni[35].x" -105.71428680419922;
	setAttr ".tgi[0].ni[35].y" -75.714286804199219;
	setAttr ".tgi[0].ni[35].nvs" 1923;
	setAttr ".tgi[0].ni[36].x" 1088.5714111328125;
	setAttr ".tgi[0].ni[36].y" 1961.4285888671875;
	setAttr ".tgi[0].ni[36].nvs" 18304;
	setAttr ".tgi[0].ni[37].x" 1702.857177734375;
	setAttr ".tgi[0].ni[37].y" -2577.142822265625;
	setAttr ".tgi[0].ni[37].nvs" 18304;
	setAttr ".tgi[0].ni[38].x" 781.4285888671875;
	setAttr ".tgi[0].ni[38].y" 1870;
	setAttr ".tgi[0].ni[38].nvs" 18304;
	setAttr ".tgi[0].ni[39].x" 1737.142822265625;
	setAttr ".tgi[0].ni[39].y" 221.42857360839844;
	setAttr ".tgi[0].ni[39].nvs" 18304;
	setAttr ".tgi[0].ni[40].x" 1395.7142333984375;
	setAttr ".tgi[0].ni[40].y" 2355.71435546875;
	setAttr ".tgi[0].ni[40].nvs" 18304;
	setAttr ".tgi[0].ni[41].x" 1702.857177734375;
	setAttr ".tgi[0].ni[41].y" 2052.857177734375;
	setAttr ".tgi[0].ni[41].nvs" 18304;
	setAttr ".tgi[0].ni[42].x" 1395.7142333984375;
	setAttr ".tgi[0].ni[42].y" 300;
	setAttr ".tgi[0].ni[42].nvs" 18304;
	setAttr ".tgi[0].ni[43].x" 474.28570556640625;
	setAttr ".tgi[0].ni[43].y" 1824.2857666015625;
	setAttr ".tgi[0].ni[43].nvs" 18304;
	setAttr ".tgi[0].ni[44].x" 781.4285888671875;
	setAttr ".tgi[0].ni[44].y" 1690;
	setAttr ".tgi[0].ni[44].nvs" 18304;
	setAttr ".tgi[0].ni[45].x" 1737.142822265625;
	setAttr ".tgi[0].ni[45].y" 344.28570556640625;
	setAttr ".tgi[0].ni[45].nvs" 18304;
	setAttr ".tgi[0].ni[46].x" -412.85714721679688;
	setAttr ".tgi[0].ni[46].y" 202.85714721679688;
	setAttr ".tgi[0].ni[46].nvs" 1923;
	setAttr ".tgi[0].ni[47].x" 1702.857177734375;
	setAttr ".tgi[0].ni[47].y" -2274.28564453125;
	setAttr ".tgi[0].ni[47].nvs" 18304;
	setAttr ".tgi[0].ni[48].x" 1702.857177734375;
	setAttr ".tgi[0].ni[48].y" 2294.28564453125;
	setAttr ".tgi[0].ni[48].nvs" 18304;
	setAttr ".tgi[0].ni[49].x" 1088.5714111328125;
	setAttr ".tgi[0].ni[49].y" 2260;
	setAttr ".tgi[0].ni[49].nvs" 18304;
	setAttr ".tgi[0].ni[50].x" -140;
	setAttr ".tgi[0].ni[50].y" 2255.71435546875;
	setAttr ".tgi[0].ni[50].nvs" 18304;
	setAttr ".tgi[0].ni[51].x" 474.28570556640625;
	setAttr ".tgi[0].ni[51].y" 2004.2857666015625;
	setAttr ".tgi[0].ni[51].nvs" 18304;
	setAttr ".tgi[0].ni[52].x" -447.14285278320313;
	setAttr ".tgi[0].ni[52].y" 2002.857177734375;
	setAttr ".tgi[0].ni[52].nvs" 18304;
	setAttr ".tgi[0].ni[53].x" 1088.5714111328125;
	setAttr ".tgi[0].ni[53].y" 1838.5714111328125;
	setAttr ".tgi[0].ni[53].nvs" 18304;
	setAttr ".tgi[0].ni[54].x" 1395.7142333984375;
	setAttr ".tgi[0].ni[54].y" 2175.71435546875;
	setAttr ".tgi[0].ni[54].nvs" 18304;
	setAttr ".tgi[0].ni[55].x" 1702.857177734375;
	setAttr ".tgi[0].ni[55].y" -1517.142822265625;
	setAttr ".tgi[0].ni[55].nvs" 18304;
	setAttr ".tgi[0].ni[56].x" 1702.857177734375;
	setAttr ".tgi[0].ni[56].y" -457.14285278320313;
	setAttr ".tgi[0].ni[56].nvs" 18304;
	setAttr ".tgi[0].ni[57].x" 1122.857177734375;
	setAttr ".tgi[0].ni[57].y" 275.71429443359375;
	setAttr ".tgi[0].ni[57].nvs" 18304;
	setAttr ".tgi[0].ni[58].x" 1395.7142333984375;
	setAttr ".tgi[0].ni[58].y" 2052.857177734375;
	setAttr ".tgi[0].ni[58].nvs" 18304;
	setAttr ".tgi[0].ni[59].x" 1702.857177734375;
	setAttr ".tgi[0].ni[59].y" -1971.4285888671875;
	setAttr ".tgi[0].ni[59].nvs" 18304;
	setAttr ".tgi[0].ni[60].x" 781.4285888671875;
	setAttr ".tgi[0].ni[60].y" 2230;
	setAttr ".tgi[0].ni[60].nvs" 18304;
	setAttr ".tgi[0].ni[61].x" 1395.7142333984375;
	setAttr ".tgi[0].ni[61].y" 1447.142822265625;
	setAttr ".tgi[0].ni[61].nvs" 18304;
	setAttr ".tgi[0].ni[62].x" -412.85714721679688;
	setAttr ".tgi[0].ni[62].y" 4.2857141494750977;
	setAttr ".tgi[0].ni[62].nvs" 1923;
	setAttr ".tgi[0].ni[63].x" 1702.857177734375;
	setAttr ".tgi[0].ni[63].y" -305.71429443359375;
	setAttr ".tgi[0].ni[63].nvs" 18304;
	setAttr ".tgi[0].ni[64].x" 1702.857177734375;
	setAttr ".tgi[0].ni[64].y" 451.42855834960938;
	setAttr ".tgi[0].ni[64].nvs" 18304;
	setAttr ".tgi[0].ni[65].x" 1430;
	setAttr ".tgi[0].ni[65].y" 98.571426391601563;
	setAttr ".tgi[0].ni[65].nvs" 18304;
	setAttr ".tgi[0].ni[66].x" 1737.142822265625;
	setAttr ".tgi[0].ni[66].y" -24.285715103149414;
	setAttr ".tgi[0].ni[66].nvs" 18304;
	setAttr ".tgi[0].ni[67].x" 1702.857177734375;
	setAttr ".tgi[0].ni[67].y" 300;
	setAttr ".tgi[0].ni[67].nvs" 18304;
	setAttr ".tgi[0].ni[68].x" 1395.7142333984375;
	setAttr ".tgi[0].ni[68].y" 602.85711669921875;
	setAttr ".tgi[0].ni[68].nvs" 18304;
	setAttr ".tgi[0].ni[69].x" 1682.857177734375;
	setAttr ".tgi[0].ni[69].y" -2.8571429252624512;
	setAttr ".tgi[0].ni[69].nvs" 18304;
	setAttr ".tgi[0].ni[70].x" 1395.7142333984375;
	setAttr ".tgi[0].ni[70].y" 148.57142639160156;
	setAttr ".tgi[0].ni[70].nvs" 18304;
	setAttr ".tgi[0].ni[71].x" 781.4285888671875;
	setAttr ".tgi[0].ni[71].y" 2410;
	setAttr ".tgi[0].ni[71].nvs" 18304;
	setAttr ".tgi[0].ni[72].x" 1122.857177734375;
	setAttr ".tgi[0].ni[72].y" -18.571428298950195;
	setAttr ".tgi[0].ni[72].nvs" 18306;
	setAttr ".tgi[0].ni[73].x" -447.14285278320313;
	setAttr ".tgi[0].ni[73].y" 1880;
	setAttr ".tgi[0].ni[73].nvs" 18304;
	setAttr ".tgi[0].ni[74].x" 1430;
	setAttr ".tgi[0].ni[74].y" 221.42857360839844;
	setAttr ".tgi[0].ni[74].nvs" 18304;
	setAttr ".tgi[0].ni[75].x" 1430;
	setAttr ".tgi[0].ni[75].y" -147.14285278320313;
	setAttr ".tgi[0].ni[75].nvs" 18304;
	setAttr ".tgi[0].ni[76].x" 1430;
	setAttr ".tgi[0].ni[76].y" 344.28570556640625;
	setAttr ".tgi[0].ni[76].nvs" 18304;
	setAttr ".tgi[0].ni[77].x" 1702.857177734375;
	setAttr ".tgi[0].ni[77].y" -1062.857177734375;
	setAttr ".tgi[0].ni[77].nvs" 18304;
select -ne :time1;
	setAttr -av -k on ".cch";
	setAttr -k on ".fzn";
	setAttr -av -cb on ".ihi";
	setAttr -av -k on ".nds";
	setAttr -cb on ".bnm";
	setAttr ".o" 1;
	setAttr -av ".unw" 1;
	setAttr -av -k on ".etw";
	setAttr -av -k on ".tps";
	setAttr -av -k on ".tms";
select -ne :hardwareRenderingGlobals;
	setAttr -av -k on ".ihi";
	setAttr ".otfna" -type "stringArray" 22 "NURBS Curves" "NURBS Surfaces" "Polygons" "Subdiv Surface" "Particles" "Particle Instance" "Fluids" "Strokes" "Image Planes" "UI" "Lights" "Cameras" "Locators" "Joints" "IK Handles" "Deformers" "Motion Trails" "Components" "Hair Systems" "Follicles" "Misc. UI" "Ornaments"  ;
	setAttr ".otfva" -type "Int32Array" 22 0 1 1 1 1 1
		 1 1 1 0 0 0 0 0 0 0 0 0
		 0 0 0 0 ;
	setAttr -k on ".hwi";
	setAttr -av ".ta";
	setAttr -av ".tq";
	setAttr -av ".etmr";
	setAttr -av ".tmr";
	setAttr -av ".aoon";
	setAttr -av ".aoam";
	setAttr -av ".aora";
	setAttr -k on ".hff";
	setAttr -av -k on ".hfd";
	setAttr -av -k on ".hfs";
	setAttr -av -k on ".hfe";
	setAttr -av ".hfc";
	setAttr -av -k on ".hfcr";
	setAttr -av -k on ".hfcg";
	setAttr -av -k on ".hfcb";
	setAttr -av ".hfa";
	setAttr -av ".mbe";
	setAttr -av -k on ".mbsof";
	setAttr -k on ".blen";
	setAttr -k on ".blat";
	setAttr -av ".msaa";
	setAttr ".fprt" yes;
select -ne :renderPartition;
	setAttr -av -k on ".cch";
	setAttr -cb on ".ihi";
	setAttr -av -k on ".nds";
	setAttr -cb on ".bnm";
	setAttr -s 18 ".st";
	setAttr -cb on ".an";
	setAttr -cb on ".pt";
select -ne :renderGlobalsList1;
	setAttr -k on ".cch";
	setAttr -cb on ".ihi";
	setAttr -k on ".nds";
	setAttr -cb on ".bnm";
select -ne :defaultShaderList1;
	setAttr -k on ".cch";
	setAttr -cb on ".ihi";
	setAttr -k on ".nds";
	setAttr -cb on ".bnm";
	setAttr -s 20 ".s";
select -ne :postProcessList1;
	setAttr -k on ".cch";
	setAttr -cb on ".ihi";
	setAttr -k on ".nds";
	setAttr -cb on ".bnm";
	setAttr -s 2 ".p";
select -ne :defaultRenderUtilityList1;
	setAttr -k on ".cch";
	setAttr -cb on ".ihi";
	setAttr -av -k on ".nds";
	setAttr -cb on ".bnm";
	setAttr -s 20 ".u";
select -ne :defaultRenderingList1;
	setAttr -k on ".ihi";
	setAttr -s 5 ".r";
select -ne :initialShadingGroup;
	setAttr -av -k on ".cch";
	setAttr -k on ".fzn";
	setAttr -cb on ".ihi";
	setAttr -av -k on ".nds";
	setAttr -cb on ".bnm";
	setAttr -k on ".bbx";
	setAttr -k on ".vwm";
	setAttr -k on ".tpv";
	setAttr -k on ".uit";
	setAttr -s 2 ".dsm";
	setAttr -k on ".mwc";
	setAttr -cb on ".an";
	setAttr -cb on ".il";
	setAttr -cb on ".vo";
	setAttr -cb on ".eo";
	setAttr -cb on ".fo";
	setAttr -cb on ".epo";
	setAttr ".ro" yes;
select -ne :initialParticleSE;
	setAttr -av -k on ".cch";
	setAttr -cb on ".ihi";
	setAttr -av -k on ".nds";
	setAttr -cb on ".bnm";
	setAttr -k on ".mwc";
	setAttr -cb on ".an";
	setAttr -cb on ".il";
	setAttr -cb on ".vo";
	setAttr -cb on ".eo";
	setAttr -cb on ".fo";
	setAttr -cb on ".epo";
	setAttr ".ro" yes;
select -ne :defaultRenderGlobals;
	setAttr -av -k on ".cch";
	setAttr -cb on ".ihi";
	setAttr -av -k on ".nds";
	setAttr -cb on ".bnm";
	setAttr -cb on ".macc";
	setAttr -cb on ".macd";
	setAttr -cb on ".macq";
	setAttr -k on ".mcfr";
	setAttr -cb on ".ifg";
	setAttr -k on ".clip";
	setAttr -k on ".edm";
	setAttr -av -k on ".edl";
	setAttr -cb on ".ren";
	setAttr -av -k on ".esr";
	setAttr -k on ".ors";
	setAttr -cb on ".sdf";
	setAttr -av -k on ".outf";
	setAttr -av -cb on ".imfkey";
	setAttr -av -k on ".gama";
	setAttr -av -cb on ".an";
	setAttr -cb on ".ar";
	setAttr -k on ".fs" 1;
	setAttr -k on ".ef" 10;
	setAttr -av -k on ".bfs";
	setAttr -cb on ".me";
	setAttr -cb on ".se";
	setAttr -av -k on ".be";
	setAttr -av -cb on ".ep";
	setAttr -k on ".fec";
	setAttr -av -k on ".ofc";
	setAttr -cb on ".ofe";
	setAttr -cb on ".efe";
	setAttr -cb on ".oft";
	setAttr -cb on ".umfn";
	setAttr -cb on ".ufe";
	setAttr -av -cb on ".pff";
	setAttr -av -cb on ".peie";
	setAttr -av -cb on ".ifp";
	setAttr -k on ".rv";
	setAttr -k on ".comp";
	setAttr -k on ".cth";
	setAttr -k on ".soll";
	setAttr -cb on ".sosl";
	setAttr -k on ".rd";
	setAttr -k on ".lp";
	setAttr -av -k on ".sp";
	setAttr -k on ".shs";
	setAttr -av -k on ".lpr";
	setAttr -cb on ".gv";
	setAttr -cb on ".sv";
	setAttr -k on ".mm";
	setAttr -av -k on ".npu";
	setAttr -k on ".itf";
	setAttr -k on ".shp";
	setAttr -cb on ".isp";
	setAttr -k on ".uf";
	setAttr -k on ".oi";
	setAttr -k on ".rut";
	setAttr -k on ".mot";
	setAttr -av -k on ".mb";
	setAttr -av -k on ".mbf";
	setAttr -k on ".mbso";
	setAttr -k on ".mbsc";
	setAttr -av -k on ".afp";
	setAttr -k on ".pfb";
	setAttr -k on ".pram";
	setAttr -k on ".poam";
	setAttr -k on ".prlm";
	setAttr -k on ".polm";
	setAttr -cb on ".prm";
	setAttr -cb on ".pom";
	setAttr -cb on ".pfrm";
	setAttr -cb on ".pfom";
	setAttr -av -k on ".bll";
	setAttr -av -k on ".bls";
	setAttr -av -k on ".smv";
	setAttr -k on ".ubc";
	setAttr -k on ".mbc";
	setAttr -cb on ".mbt";
	setAttr -k on ".udbx";
	setAttr -k on ".smc";
	setAttr -k on ".kmv";
	setAttr -cb on ".isl";
	setAttr -cb on ".ism";
	setAttr -cb on ".imb";
	setAttr -av -k on ".rlen";
	setAttr -av -k on ".frts";
	setAttr -k on ".tlwd";
	setAttr -k on ".tlht";
	setAttr -k on ".jfc";
	setAttr -cb on ".rsb";
	setAttr -cb on ".ope";
	setAttr -cb on ".oppf";
	setAttr -av -k on ".rcp";
	setAttr -av -k on ".icp";
	setAttr -av -k on ".ocp";
	setAttr -cb on ".hbl";
select -ne :defaultResolution;
	setAttr -av -k on ".cch";
	setAttr -av -k on ".ihi";
	setAttr -av -k on ".nds";
	setAttr -k on ".bnm";
	setAttr -av -k on ".w";
	setAttr -av -k on ".h";
	setAttr -av ".pa" 1;
	setAttr -av -k on ".al";
	setAttr -av -k on ".dar";
	setAttr -av -k on ".ldar";
	setAttr -av -k on ".dpi";
	setAttr -av -k on ".off";
	setAttr -av -k on ".fld";
	setAttr -av -k on ".zsl";
	setAttr -av -k on ".isu";
	setAttr -av -k on ".pdu";
select -ne :hardwareRenderGlobals;
	setAttr -av -k on ".cch";
	setAttr -cb on ".ihi";
	setAttr -av -k on ".nds";
	setAttr -cb on ".bnm";
	setAttr -av ".ctrs" 256;
	setAttr -av ".btrs" 512;
	setAttr -av -k off -cb on ".fbfm";
	setAttr -av -k off -cb on ".ehql";
	setAttr -av -k off -cb on ".eams";
	setAttr -av -k off -cb on ".eeaa";
	setAttr -av -k off -cb on ".engm";
	setAttr -av -k off -cb on ".mes";
	setAttr -av -k off -cb on ".emb";
	setAttr -av -k off -cb on ".mbbf";
	setAttr -av -k off -cb on ".mbs";
	setAttr -av -k off -cb on ".trm";
	setAttr -av -k off -cb on ".tshc";
	setAttr -av -k off -cb on ".enpt";
	setAttr -av -k off -cb on ".clmt";
	setAttr -av -k off -cb on ".tcov";
	setAttr -av -k off -cb on ".lith";
	setAttr -av -k off -cb on ".sobc";
	setAttr -av -k off -cb on ".cuth";
	setAttr -av -k off -cb on ".hgcd";
	setAttr -av -k off -cb on ".hgci";
	setAttr -av -k off -cb on ".mgcs";
	setAttr -av -k off -cb on ".twa";
	setAttr -av -k off -cb on ".twz";
	setAttr -cb on ".hwcc";
	setAttr -cb on ".hwdp";
	setAttr -cb on ".hwql";
	setAttr -k on ".hwfr";
	setAttr -k on ".soll";
	setAttr -k on ".sosl";
	setAttr -k on ".bswa";
	setAttr -k on ".shml";
	setAttr -k on ".hwel";
connectAttr "locator3.t" "learning_vector_objectRN1.phl[1]";
connectAttr "locator1.t" "learning_vector_object1RN.phl[1]";
connectAttr "vec_C.o" "learning_vector_object1RN.phl[2]";
connectAttr "learning_vector_object1RN.phl[3]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[72].dn"
		;
connectAttr "learning_vector_object1RN.phl[4]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[30].dn"
		;
connectAttr "learning_vector_object1RN.phl[5]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[75].dn"
		;
connectAttr "learning_vector_object2RN.phl[1]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[13].dn"
		;
connectAttr "learning_vector_object2RN.phl[2]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[50].dn"
		;
connectAttr "learning_vector_object2RN.phl[3]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[18].dn"
		;
connectAttr "learning_vector_object2RN.phl[4]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[73].dn"
		;
connectAttr "learning_vector_object2RN.phl[5]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[25].dn"
		;
connectAttr "learning_vector_object2RN.phl[6]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[5].dn"
		;
connectAttr "learning_vector_object2RN.phl[7]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[61].dn"
		;
connectAttr "learning_vector_object2RN.phl[8]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[52].dn"
		;
connectAttr "learning_vector_object2RN.phl[9]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[27].dn"
		;
connectAttr "learning_vector_object2RN.phl[10]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[20].dn"
		;
connectAttr "vec_D.o" "learning_vector_object2RN.phl[11]";
connectAttr "learning_vector_object2RN.phl[12]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[4].dn"
		;
connectAttr "learning_vector_object2RN.phl[13]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[76].dn"
		;
connectAttr "learning_vector_object2RN.phl[14]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[10].dn"
		;
connectAttr "learning_vector_object2RN.phl[15]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[45].dn"
		;
connectAttr "learning_vector_object2RN.phl[16]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[77].dn"
		;
connectAttr "learning_vector_object2RN.phl[17]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[31].dn"
		;
connectAttr "learning_vector_object2RN.phl[18]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[3].dn"
		;
connectAttr "learning_vector_object2RN.phl[19]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[64].dn"
		;
connectAttr "learning_vector_object2RN.phl[20]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[21].dn"
		;
connectAttr "learning_vector_object2RN.phl[21]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[1].dn"
		;
connectAttr "learning_vector_object2RN.phl[22]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[55].dn"
		;
connectAttr "learning_vector_object2RN.phl[23]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[68].dn"
		;
connectAttr "learning_vector_object2RN.phl[24]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[16].dn"
		;
connectAttr "learning_vector_object2RN.phl[25]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[7].dn"
		;
connectAttr "learning_vector_object2RN.phl[26]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[11].dn"
		;
connectAttr "learning_vector_object2RN.phl[27]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[66].dn"
		;
connectAttr "learning_vector_object2RN.phl[28]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[53].dn"
		;
connectAttr "learning_vector_object2RN.phl[29]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[63].dn"
		;
connectAttr "learning_vector_object2RN.phl[30]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[2].dn"
		;
connectAttr "learning_vector_object2RN.phl[31]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[36].dn"
		;
connectAttr "learning_vector_object2RN.phl[32]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[32].dn"
		;
connectAttr "learning_vector_object2RN.phl[33]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[6].dn"
		;
connectAttr "learning_vector_object2RN.phl[34]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[39].dn"
		;
connectAttr "learning_vector_object2RN.phl[35]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[49].dn"
		;
connectAttr "learning_vector_object2RN.phl[36]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[56].dn"
		;
connectAttr "learning_vector_object2RN.phl[37]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[22].dn"
		;
connectAttr "learning_vector_object2RN.phl[38]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[47].dn"
		;
connectAttr "learning_vector_object2RN.phl[39]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[29].dn"
		;
connectAttr "learning_vector_object2RN.phl[40]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[70].dn"
		;
connectAttr "learning_vector_object2RN.phl[41]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[24].dn"
		;
connectAttr "learning_vector_object2RN.phl[42]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[59].dn"
		;
connectAttr "learning_vector_object2RN.phl[43]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[69].dn"
		;
connectAttr "learning_vector_object2RN.phl[44]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[42].dn"
		;
connectAttr "learning_vector_object2RN.phl[45]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[67].dn"
		;
connectAttr "learning_vector_object2RN.phl[46]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[14].dn"
		;
connectAttr "learning_vector_object2RN.phl[47]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[33].dn"
		;
connectAttr "learning_vector_object2RN.phl[48]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[57].dn"
		;
connectAttr "learning_vector_object2RN.phl[49]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[8].dn"
		;
connectAttr "learning_vector_object2RN.phl[50]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[43].dn"
		;
connectAttr "learning_vector_object2RN.phl[51]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[38].dn"
		;
connectAttr "learning_vector_object2RN.phl[52]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[44].dn"
		;
connectAttr "learning_vector_object2RN.phl[53]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[34].dn"
		;
connectAttr "learning_vector_object2RN.phl[54]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[40].dn"
		;
connectAttr "learning_vector_object2RN.phl[55]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[48].dn"
		;
connectAttr "learning_vector_object2RN.phl[56]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[54].dn"
		;
connectAttr "learning_vector_object2RN.phl[57]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[41].dn"
		;
connectAttr "learning_vector_object2RN.phl[58]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[17].dn"
		;
connectAttr "learning_vector_object2RN.phl[59]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[65].dn"
		;
connectAttr "learning_vector_object2RN.phl[60]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[74].dn"
		;
connectAttr "learning_vector_object2RN.phl[61]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[51].dn"
		;
connectAttr "learning_vector_object2RN.phl[62]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[15].dn"
		;
connectAttr "learning_vector_object2RN.phl[63]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[12].dn"
		;
connectAttr "learning_vector_object2RN.phl[64]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[28].dn"
		;
connectAttr "learning_vector_object2RN.phl[65]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[19].dn"
		;
connectAttr "learning_vector_object2RN.phl[66]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[60].dn"
		;
connectAttr "learning_vector_object2RN.phl[67]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[71].dn"
		;
connectAttr "learning_vector_object2RN.phl[68]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[58].dn"
		;
relationship "link" ":lightLinker1" ":initialShadingGroup.message" ":defaultLightSet.message";
relationship "link" ":lightLinker1" ":initialParticleSE.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" ":initialShadingGroup.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" ":initialParticleSE.message" ":defaultLightSet.message";
connectAttr "layerManager.dli[0]" "defaultLayer.id";
connectAttr "renderLayerManager.rlmi[0]" "defaultRenderLayer.rlid";
connectAttr "locator2.t" "vec_A.i3[0]";
connectAttr "locator1.t" "vec_A.i3[1]";
connectAttr "locator3.t" "vec_B.i3[0]";
connectAttr "locator1.t" "vec_B.i3[1]";
connectAttr "sharedReferenceNode.sr" "learning_vector_objectRN1.sr";
connectAttr "vec_A.o3" "vec_C.i1";
connectAttr "vec_B.o3" "vec_C.i2";
connectAttr "vec_C.o" "vec_D.i1";
connectAttr "vec_A.o3" "vec_D.i2";
connectAttr "vec_A.msg" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[0].dn";
connectAttr "locator3.msg" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[9].dn";
connectAttr "vec_C.msg" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[23].dn";
connectAttr "vec_D.msg" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[26].dn";
connectAttr "vec_B.msg" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[35].dn";
connectAttr "learning_vector_object2RN.msg" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[37].dn"
		;
connectAttr "locator2.msg" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[46].dn";
connectAttr "locator1.msg" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[62].dn";
connectAttr "vec_A.msg" ":defaultRenderUtilityList1.u" -na;
connectAttr "vec_B.msg" ":defaultRenderUtilityList1.u" -na;
connectAttr "vec_C.msg" ":defaultRenderUtilityList1.u" -na;
connectAttr "vec_D.msg" ":defaultRenderUtilityList1.u" -na;
connectAttr "defaultRenderLayer.msg" ":defaultRenderingList1.r" -na;
connectAttr "pPlaneShape1.iog" ":initialShadingGroup.dsm" -na;
connectAttr "pCubeShape1.iog" ":initialShadingGroup.dsm" -na;
// End of 01_vector_04_cross product.ma
