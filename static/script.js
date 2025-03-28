// Toggle logging here
const DEBUG = true;
const log = (...args) => {
	if (DEBUG) console.log(...args);
};

let selectedStaticImage = null;

async function loadSettings() {
	const res = await fetch("/get_settings");
	const settings = await res.json();

	document.getElementById("themeSelect").value = settings.theme || "";
	document.getElementById("duration").value = settings.duration || 2;
	document.getElementById("sleepEnable").checked =
		settings.sleep_enable || false;
	document.getElementById("sleepStart").value =
		settings.sleep_range?.start || "00:00";
	document.getElementById("sleepEnd").value =
		settings.sleep_range?.end || "09:00";

	selectedStaticImage = settings.static_image || null;
	loadThemePreviews(settings.theme);
}

async function saveSettings() {
	const payload = {
		theme: document.getElementById("themeSelect").value,
		duration: parseFloat(document.getElementById("duration").value),
		sleep_enable: document.getElementById("sleepEnable").checked,
		sleep_range: {
			start: document.getElementById("sleepStart").value,
			end: document.getElementById("sleepEnd").value,
		},
		mode: "all",
		static_image: selectedStaticImage,
	};

	await fetch("/set_settings", {
		method: "POST",
		headers: { "Content-Type": "application/json" },
		body: JSON.stringify(payload),
	});

	const alertBox = document.getElementById("alertBox");
	alertBox.classList.remove("d-none");
	setTimeout(() => alertBox.classList.add("d-none"), 3000);
}

async function loadThemes() {
	const res = await fetch("/get_themes");
	const data = await res.json();

	const themes = Array.isArray(data.themes) ? data.themes : [];

	const mainThemeSelect = document.getElementById("themeSelect");
	const uploadThemeSelect = document.getElementById("themeSelectUpload");

	mainThemeSelect.innerHTML = `<option value="">-- Select a Theme --</option>`;
	themes.forEach((theme) => {
		const option = document.createElement("option");
		option.value = theme;
		option.text = theme;
		mainThemeSelect.appendChild(option);
	});

	uploadThemeSelect.innerHTML = `<option value="">-- Select a Theme --</option>`;
	themes.forEach((theme) => {
		const option = document.createElement("option");
		option.value = theme;
		option.text = theme;
		uploadThemeSelect.appendChild(option);
	});

	const createNewOption = document.createElement("option");
	createNewOption.value = "__new__";
	createNewOption.text = "➕ Create New Theme...";
	uploadThemeSelect.appendChild(createNewOption);
}

function toggleNewThemeInput() {
	const themeSelect = document.getElementById("themeSelectUpload");
	const newThemeWrapper = document.getElementById("newThemeWrapper");

	if (themeSelect.value === "__new__") {
		newThemeWrapper.classList.remove("d-none");
	} else {
		newThemeWrapper.classList.add("d-none");
		document.getElementById("newThemeName").value = "";
	}
}

async function uploadImage() {
	const fileInput = document.getElementById("fileInput");
	const themeSelect = document.getElementById("themeSelectUpload");
	const newThemeInput = document.getElementById("newThemeName");
	const formData = new FormData();

	if (!fileInput.files[0]) {
		alert("Please choose an image.");
		return;
	}

	formData.append("file", fileInput.files[0]);

	if (themeSelect.value === "__new__") {
		const newTheme = newThemeInput.value.trim();
		if (!newTheme) {
			alert("Please enter a name for the new theme.");
			return;
		}
		formData.append("new_theme", newTheme);
	} else if (themeSelect.value) {
		formData.append("theme", themeSelect.value);
	} else {
		alert("Please select a theme or create a new one.");
		return;
	}

	const res = await fetch("/upload_image", {
		method: "POST",
		body: formData,
	});

	const data = await res.json();
	alert("Uploaded to theme: " + data.theme);
	await loadThemes();
}

async function loadThemePreviews(theme) {
	const container = document.getElementById("imagePreviewGrid");
	container.innerHTML = "";
	selectedStaticImage = null;

	if (!theme) return;

	const res = await fetch(`/get_theme_images/${theme}`);
	const data = await res.json();

	const cycleCol = document.createElement("div");
	cycleCol.className = "col-3";
	const cycleBox = document.createElement("div");
	cycleBox.className =
		"img-thumbnail preview-img d-flex align-items-center justify-content-center text-center bg-secondary text-white";
	cycleBox.style.cursor = "pointer";
	cycleBox.textContent = "Cycle Images";
	cycleBox.onclick = () => {
		selectedStaticImage = null;
		document
			.querySelectorAll("#imagePreviewGrid .img-thumbnail")
			.forEach((i) => {
				i.classList.remove("border-primary", "border", "border-3");
			});
		cycleBox.classList.add("border-primary", "border", "border-3");
	};
	cycleCol.appendChild(cycleBox);
	container.appendChild(cycleCol);

	data.images.forEach((filename) => {
		const url = `/themes/${theme}/${filename}`;

		const col = document.createElement("div");
		col.className = "col-3";

		const img = document.createElement("img");
		img.src = url;
		img.alt = filename;
		img.className = "img-thumbnail preview-img";
		img.style.cursor = "pointer";

		if (filename === selectedStaticImage) {
			img.classList.add("border-primary", "border", "border-3");
		}

		img.onclick = () => {
			selectedStaticImage = filename;
			document
				.querySelectorAll("#imagePreviewGrid .img-thumbnail")
				.forEach((i) => {
					i.classList.remove("border-primary", "border", "border-3");
				});
			img.classList.add("border-primary", "border", "border-3");
		};

		col.appendChild(img);
		container.appendChild(col);
	});
}

window.onload = async () => {
	await loadThemes();
	await loadSettings();
};
