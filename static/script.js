// Enable or disable debug logging
var DEBUG = true;

/**
 * Log messages to console if DEBUG is true.
 */
function debugLog(...args) {
	if (DEBUG) {
		console.log(...args);
	}
}

// Track current selected theme and image
var currentTheme = null;
var currentImage = null;

/**
 * Load available themes from the server and populate the theme dropdown.
 */
function loadThemes() {
	debugLog("Loading themes from /get_themes");
	return fetch("/get_themes")
		.then((response) => {
			if (!response.ok) throw new Error("Failed to load themes");
			return response.json();
		})
		.then((themes) => {
			debugLog("Available themes:", themes);
			var select = document.getElementById("themeSelect");
			if (!select) return;
			// Clear existing options
			select.innerHTML = "";
			// Populate dropdown with theme names
			themes.forEach((theme) => {
				var opt = document.createElement("option");
				opt.value = theme;
				opt.textContent = theme;
				select.appendChild(opt);
			});
		})
		.catch((error) => {
			console.error("Error loading themes:", error);
		});
}

/**
 * Load all images for a given theme and display them as thumbnails.
 * @param {string} theme - The theme name to load images from.
 */
function loadThemeImages(theme) {
	debugLog("Loading images for theme:", theme);
	var container = document.getElementById("imagesContainer");
	if (!container) {
		return Promise.resolve(); // No container to display images
	}
	// Optional: show a loading indicator
	container.textContent = "Loading images...";
	return fetch("/get_theme_images/" + encodeURIComponent(theme))
		.then((response) => {
			if (!response.ok)
				throw new Error("Failed to load images for theme " + theme);
			return response.json();
		})
		.then((images) => {
			debugLog(`Images for theme "${theme}":`, images);
			container.innerHTML = ""; // Clear any existing images
			if (!images || images.length === 0) {
				container.textContent = "No images available.";
				return;
			}
			// Create an <img> element for each image
			images.forEach((imageName) => {
				var imgElem = document.createElement("img");
				// Assume images are served from a static directory by theme
				imgElem.src =
					"/static/themes/" +
					encodeURIComponent(theme) +
					"/" +
					encodeURIComponent(imageName);
				imgElem.alt = imageName;
				imgElem.classList.add("img-thumbnail", "theme-image");
				// Store the image name and theme in data attributes for selection
				imgElem.setAttribute("data-image", imageName);
				imgElem.setAttribute("data-theme", theme);
				container.appendChild(imgElem);
			});
		})
		.catch((error) => {
			console.error("Error loading images for theme:", error);
			container.textContent = "Error loading images.";
		});
}

/**
 * Highlight the thumbnail corresponding to the given image name.
 * Removes highlight from any previously selected image.
 * @param {string} imageName - The file name of the image to highlight.
 */
function highlightImage(imageName) {
	var container = document.getElementById("imagesContainer");
	if (!container) return;
	// Remove existing highlight
	var prev = container.querySelector(".img-thumbnail.selected");
	if (prev) {
		prev.classList.remove("selected");
	}
	// Add highlight to the new selected image
	var newImg = null;
	var thumbnails = container.querySelectorAll(".img-thumbnail[data-image]");
	for (var img of thumbnails) {
		if (img.getAttribute("data-image") === imageName) {
			newImg = img;
			break;
		}
	}
	if (newImg) {
		newImg.classList.add("selected");
	}
}

/**
 * Load current settings from the server and initialize the UI (select theme and highlight image).
 */
function loadSettings() {
	debugLog("Loading settings from /get_settings");
	return fetch("/get_settings")
		.then((response) => {
			if (!response.ok) throw new Error("Failed to load settings");
			return response.json();
		})
		.then((settings) => {
			debugLog("Current settings:", settings);
			if (!settings) return;
			// If a theme is specified in settings, select it and load its images
			if (settings.theme) {
				currentTheme = settings.theme;
				var themeSelect = document.getElementById("themeSelect");
				if (themeSelect) {
					themeSelect.value = settings.theme;
				}
				// Load images for the current theme, then highlight the current image
				return loadThemeImages(settings.theme).then(() => {
					if (settings.image) {
						currentImage = settings.image;
						highlightImage(settings.image);
					}
				});
			}
		})
		.catch((error) => {
			console.error("Error loading settings:", error);
		});
}

/**
 * Save the current settings (selected theme and image) to the server.
 */
function saveSettings() {
	debugLog("Saving settings to /set_settings");
	var data = {};
	if (currentTheme) data.theme = currentTheme;
	if (currentImage) data.image = currentImage;
	fetch("/set_settings", {
		method: "POST",
		headers: { "Content-Type": "application/json" },
		body: JSON.stringify(data),
	})
		.then((response) => {
			if (!response.ok) throw new Error("Settings save failed");
			return response.json();
		})
		.then((result) => {
			debugLog("Settings saved successfully.", result);
		})
		.catch((error) => {
			console.error("Error saving settings:", error);
		});
}

/**
 * Upload a new image to the server, either adding to an existing theme or creating a new theme.
 * Expects an input with id="imageUploadInput" for the file,
 * a select with id="themeSelect" for existing theme,
 * and an optional text input with id="newThemeInput" for a new theme name.
 */
function uploadImage() {
	var fileInput = document.getElementById("imageUploadInput");
	if (!fileInput || !fileInput.files.length) {
		console.error("No image file selected for upload");
		return;
	}
	var file = fileInput.files[0];
	// Determine target theme: use new theme name if provided, otherwise selected theme
	var newThemeInput = document.getElementById("newThemeInput");
	var newThemeName = newThemeInput ? newThemeInput.value.trim() : "";
	var themeSelect = document.getElementById("themeSelect");
	var existingTheme = themeSelect ? themeSelect.value : "";
	var targetTheme = newThemeName || existingTheme;
	if (!targetTheme) {
		console.error("No theme specified for image upload");
		return;
	}
	debugLog(
		"Uploading image to theme:",
		targetTheme,
		newThemeName ? "(new theme)" : "(existing theme)"
	);
	// Prepare form data for upload
	var formData = new FormData();
	formData.append("image", file);
	formData.append("theme", targetTheme);
	if (newThemeName) {
		// Indicate this is a new theme
		formData.append("new_theme", newThemeName);
	}
	fetch("/upload_image", {
		method: "POST",
		body: formData,
	})
		.then((response) => {
			if (!response.ok) throw new Error("Image upload failed");
			return response.json();
		})
		.then((result) => {
			debugLog("Upload successful:", result);
			// If a new theme was created, refresh the theme list and select the new theme
			if (newThemeName) {
				loadThemes().then(() => {
					if (themeSelect) {
						themeSelect.value = targetTheme;
					}
					currentTheme = targetTheme;
					currentImage = null;
					// Load images for the new theme (should include the uploaded image)
					loadThemeImages(targetTheme);
				});
			} else {
				// If added to an existing theme, reload images for that theme
				currentTheme = targetTheme;
				currentImage = null;
				loadThemeImages(targetTheme);
			}
			// Clear the file input and new theme field
			if (newThemeInput) newThemeInput.value = "";
			fileInput.value = "";
		})
		.catch((error) => {
			console.error("Error uploading image:", error);
		});
}

// Set up event handlers after the DOM is fully loaded
document.addEventListener("DOMContentLoaded", function () {
	debugLog("Initializing LED sign UI script");
	// Handle theme selection changes
	var themeSelect = document.getElementById("themeSelect");
	if (themeSelect) {
		themeSelect.addEventListener("change", function () {
			var theme = themeSelect.value;
			debugLog("Theme changed by user to:", theme);
			if (theme) {
				currentTheme = theme;
				currentImage = null;
				loadThemeImages(theme);
			}
		});
	}
	// Handle thumbnail image click (delegation)
	var imagesContainer = document.getElementById("imagesContainer");
	if (imagesContainer) {
		imagesContainer.addEventListener("click", function (e) {
			if (e.target && e.target.classList.contains("theme-image")) {
				var imgElem = e.target;
				var imageName = imgElem.getAttribute("data-image");
				var themeName = imgElem.getAttribute("data-theme");
				if (themeName) currentTheme = themeName;
				if (imageName) {
					currentImage = imageName;
					debugLog("Image selected:", imageName, "from theme:", themeName);
					highlightImage(imageName);
				}
			}
		});
	}
	// Handle save settings button
	var saveBtn = document.getElementById("saveButton");
	if (saveBtn) {
		saveBtn.addEventListener("click", function (e) {
			e.preventDefault();
			saveSettings();
		});
	}
	// Handle image upload form submission or button
	var uploadForm = document.getElementById("uploadForm");
	if (uploadForm) {
		uploadForm.addEventListener("submit", function (e) {
			e.preventDefault();
			uploadImage();
		});
	}
	var uploadBtn = document.getElementById("uploadButton");
	if (uploadBtn) {
		uploadBtn.addEventListener("click", function (e) {
			e.preventDefault();
			uploadImage();
		});
	}
	// Initial load: get themes and settings
	loadThemes().then(() => {
		// After themes are loaded, fetch and apply current settings
		loadSettings();
	});
});
