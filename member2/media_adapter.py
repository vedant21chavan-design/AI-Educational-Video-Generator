def vgp_to_media_request(packet):

    scenes = []

    for scene in packet.scenes:

        scenes.append({
            "scene_id": scene.scene_id,
            "text": scene.narration,
            "image_prompt": scene.visual_prompt,
            "duration": scene.duration
        })

    return {
        "scenes": scenes
    }