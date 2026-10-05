shader_type sky;
render_mode disable_fog;

// Original, static window-view study for Godot 4.6 Compatibility.
// Keep one world-oriented sky for every room. No camera-local panoramas.
// The visible pass reads a cached cubemap; see SPACE_VIEW_COMPOSITION.json
// for the required zero-contribution ambient routing in Compatibility.
uniform bool use_radiance_cache = true;
uniform float view_energy : hint_range(0.0, 2.0) = 1.0;
uniform float star_strength : hint_range(0.0, 1.5) = 0.75;
uniform float dust_strength : hint_range(0.0, 1.0) = 0.35;

// Azimuth is measured from +X toward +Z; +Y is up. Directions are
// normalized below so the editor can make bounded composition trials.
// Starboard: azimuth +12 degrees, elevation -17, angular radius 29.
uniform vec3 starboard_direction = vec3(0.9354072, -0.2923717, 0.1988269);
uniform float starboard_radius_degrees : hint_range(18.0, 36.0) = 29.0;
// Port: azimuth -173 degrees, elevation +6, angular radius 7.
uniform vec3 port_direction = vec3(-0.9871089, 0.1045285, -0.1212017);
uniform float port_radius_degrees : hint_range(3.0, 12.0) = 7.0;

// Shared fictional illumination direction, used only to paint the bodies.
// It is deliberately not a DirectionalLight3D or indoor light source.
const vec3 BODY_LIGHT = vec3(-0.5014059, 0.6016871, -0.6217433);

float cell_hash(vec3 p) {
	// Small bounded inputs, deterministic, with no time-based twinkle.
	return fract(sin(dot(p, vec3(17.13, 57.71, 113.53))) * 43758.5453);
}

float value_noise(vec3 p) {
	vec3 i = floor(p);
	vec3 f = fract(p);
	vec3 u = f * f * (3.0 - 2.0 * f);
	float a = mix(cell_hash(i), cell_hash(i + vec3(1.0, 0.0, 0.0)), u.x);
	float b = mix(cell_hash(i + vec3(0.0, 1.0, 0.0)), cell_hash(i + vec3(1.0, 1.0, 0.0)), u.x);
	float c = mix(cell_hash(i + vec3(0.0, 0.0, 1.0)), cell_hash(i + vec3(1.0, 0.0, 1.0)), u.x);
	float d = mix(cell_hash(i + vec3(0.0, 1.0, 1.0)), cell_hash(i + vec3(1.0, 1.0, 1.0)), u.x);
	return mix(mix(a, b, u.y), mix(c, d, u.y), u.z);
}

vec3 sparse_stars(vec3 direction) {
	// One bounded evaluation per cubemap cell, no catalogue loop. Stars
	// stay inset from cell edges; no full-screen glitter or fake lens flares.
	vec3 a = abs(direction);
	vec2 face_uv;
	float face_id;
	if (a.x >= a.y && a.x >= a.z) {
		face_uv = direction.zy / a.x;
		face_id = direction.x > 0.0 ? 0.0 : 1.0;
	} else if (a.y >= a.z) {
		face_uv = direction.xz / a.y;
		face_id = direction.y > 0.0 ? 2.0 : 3.0;
	} else {
		face_uv = direction.xy / a.z;
		face_id = direction.z > 0.0 ? 4.0 : 5.0;
	}
	vec2 grid = (face_uv * 0.5 + 0.5) * 42.0;
	vec3 key = vec3(floor(grid), face_id * 19.0 + 3.0);
	float choice = cell_hash(key);
	if (choice < 0.965) {
		return vec3(0.0);
	}
	vec2 centre = vec2(cell_hash(key + vec3(9.0, 2.0, 7.0)), cell_hash(key + vec3(1.0, 8.0, 4.0)));
	centre = 0.27 + centre * 0.46;
	float brightness = cell_hash(key + vec3(2.0, 3.0, 11.0));
	float radius = mix(0.12, 0.235, brightness * brightness);
	float distance_to_star = length(fract(grid) - centre);
	float core = 1.0 - smoothstep(radius * 0.28, radius, distance_to_star);
	vec3 tint = mix(vec3(0.63, 0.70, 0.78), vec3(0.84, 0.78, 0.65), cell_hash(key + vec3(17.0)));
	return tint * core * mix(0.35, 1.0, brightness) * star_strength;
}

vec3 quiet_background(vec3 direction) {
	vec3 colour = vec3(0.008, 0.012, 0.021);
	// A narrow, incomplete dusty belt, not an all-sky luminous wash.
	float belt = 1.0 - smoothstep(0.035, 0.20, abs(dot(direction, normalize(vec3(0.16, 0.91, 0.38)))));
	float broad = value_noise(direction * 3.6 + vec3(12.0, 4.0, 9.0));
	float detail = value_noise(direction * 12.0 + vec3(2.0, 17.0, 5.0));
	float broken = smoothstep(0.37, 0.76, broad) * mix(0.4, 1.0, detail);
	vec3 dust = mix(vec3(0.028, 0.042, 0.060), vec3(0.062, 0.039, 0.031), broad);
	colour += dust * belt * broken * dust_strength;
	return colour + sparse_stars(direction);
}

vec3 starboard_planet(vec3 direction, vec3 background) {
	vec3 centre = normalize(starboard_direction);
	float radius = radians(starboard_radius_degrees);
	float cosine_radius = cos(radius);
	float alignment = dot(direction, centre);
	float outer_cosine = cos(radius + radians(0.85));
	if (alignment < outer_cosine) {
		return background;
	}
	// Analytic ray/sphere intersection, observer outside a unit-distance
	// sphere. This supplies real curvature and surface-normal shading.
	float discriminant = max(alignment * alignment - cosine_radius * cosine_radius, 0.0);
	float hit_distance = alignment - sqrt(discriminant);
	vec3 normal = normalize(direction * hit_distance - centre);
	float incidence = dot(normal, BODY_LIGHT);
	float day = smoothstep(-0.07, 0.20, incidence);
	float diffuse = pow(max(incidence, 0.0), 0.65);
	float broad = value_noise(normal * 3.8 + vec3(11.0, 4.0, 2.0));
	float middle = value_noise(normal * 10.0 + vec3(7.0, 21.0, 3.0));
	float fine = value_noise(normal * 27.0 + vec3(3.0, 8.0, 16.0));
	float swath = smoothstep(0.40, 0.67, broad * 0.70 + middle * 0.30);
	vec3 surface_colour = mix(vec3(0.15, 0.26, 0.31), vec3(0.40, 0.38, 0.31), swath);
	surface_colour *= mix(0.82, 1.12, middle);
	// Broken, broad pale marbling remains readable at 640x360. It does
	// not identify continents, settlements, a real planet or story canon.
	float ribbon = 0.5 + 0.5 * sin(normal.y * 23.0 + broad * 9.0 + middle * 3.0);
	float veil = smoothstep(0.69, 0.90, ribbon) * smoothstep(0.32, 0.65, fine) * 0.38;
	surface_colour = mix(surface_colour, vec3(0.58, 0.61, 0.61), veil);
	vec3 night = vec3(0.013, 0.021, 0.030);
	vec3 body = mix(night, surface_colour * (0.20 + 0.80 * diffuse), day);
	float grazing = pow(1.0 - clamp(dot(normal, -direction), 0.0, 1.0), 3.0);
	body += vec3(0.085, 0.16, 0.19) * grazing * day;
	float coverage = smoothstep(cosine_radius - 0.0012, cosine_radius + 0.0012, alignment);
	float halo = smoothstep(outer_cosine, cosine_radius, alignment) * (1.0 - coverage);
	background += vec3(0.035, 0.070, 0.086) * halo * day;
	// Opaque body hides stars; no star points are painted over its face.
	return mix(background, body, coverage);
}

vec3 port_crescent(vec3 direction, vec3 background) {
	vec3 centre = normalize(port_direction);
	float radius = radians(port_radius_degrees);
	float cosine_radius = cos(radius);
	float alignment = dot(direction, centre);
	if (alignment < cosine_radius - 0.0006) {
		return background;
	}
	float discriminant = max(alignment * alignment - cosine_radius * cosine_radius, 0.0);
	float hit_distance = alignment - sqrt(discriminant);
	vec3 normal = normalize(direction * hit_distance - centre);
	float incidence = dot(normal, BODY_LIGHT);
	float day = smoothstep(-0.035, 0.10, incidence);
	float texture_value = value_noise(normal * 8.0 + vec3(31.0, 7.0, 19.0));
	vec3 lit = mix(vec3(0.26, 0.27, 0.27), vec3(0.44, 0.42, 0.37), texture_value);
	lit *= 0.20 + 0.80 * pow(max(incidence, 0.0), 0.58);
	vec3 body = mix(vec3(0.010, 0.014, 0.020), lit, day);
	float coverage = smoothstep(cosine_radius - 0.0006, cosine_radius + 0.0006, alignment);
	return mix(background, body, coverage);
}

vec3 compose_space(vec3 direction) {
	vec3 colour = quiet_background(direction);
	colour = starboard_planet(direction, colour);
	colour = port_crescent(direction, colour);
	return clamp(colour * view_energy, vec3(0.0), vec3(0.92));
}

void sky() {
	if (AT_CUBEMAP_PASS) {
		COLOR = compose_space(normalize(EYEDIR));
	} else if (use_radiance_cache) {
		// No procedural texture work in normal cached background drawing.
		COLOR = textureLod(RADIANCE, EYEDIR, 0.0).rgb;
	} else {
		// Explicit diagnostic fallback: same world-space composition, but
		// procedural work now runs per visible sky pixel. No cache claim.
		COLOR = compose_space(normalize(EYEDIR));
	}
}
