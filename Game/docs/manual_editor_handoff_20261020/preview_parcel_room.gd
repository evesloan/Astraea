extends SceneTree
const HERE="res://docs/manual_editor_handoff_20261020/"
var frames:=0
var camera:Camera3D
func _initialize()->void:call_deferred("run")
func run()->void:
	var scene:Node3D=load(HERE+"ParcelRoom_R064_Authored.tscn").instantiate();root.add_child(scene)
	var environment:=WorldEnvironment.new();environment.environment=Environment.new()
	environment.environment.background_mode=Environment.BG_COLOR
	environment.environment.background_color=Color(.07,.08,.1)
	environment.environment.ambient_light_source=Environment.AMBIENT_SOURCE_COLOR
	environment.environment.ambient_light_color=Color(.8,.85,1);environment.environment.ambient_light_energy=.5
	root.add_child(environment)
	# Preview-only lighting; saved source emitters remain budget-held in authored file.
	for light in scene.find_children("*","Light3D",true,false):light.visible=true;light.shadow_enabled=true
	camera=Camera3D.new();root.add_child(camera);camera.position=Vector3(5.3,3.5,5.1);camera.look_at(Vector3(-2.2,1.7,-1.5));camera.fov=80
	camera.current=true
	root.size=Vector2i(1280,720)
	var layer:=CanvasLayer.new();root.add_child(layer)
	var label:=Label.new();label.text="R064 PARCEL ROOM | SAVED AUTHORING SCENE | NOT INSTALLED\nPreview-only lights enabled; original scene keeps source-budget ownership.";label.position=Vector2(14,12);layer.add_child(label)
	RenderingServer.frame_post_draw.connect(capture)
func capture()->void:
	frames+=1
	if frames==30:
		var image:=root.get_texture().get_image()
		assert(image.save_png(HERE+"PARCEL_ROOM_SAVED_SCENE_PREVIEW.png")==OK)
		print("PARCEL_PREVIEW_CAPTURED")
	if frames>=120:quit()
