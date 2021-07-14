//Restore saved theme
setSlider()
loadTheme()

//Get the saved theme from local storage
function readSavedTheme() {
  let theme = window.localStorage['theme'];
  if (theme == undefined) {
    window.localStorage['theme'] = 'dark';
    theme = 'dark'
  }
  return theme
}

//Set the slider to the correct position, matching the theme
function setSlider() {
  let theme = readSavedTheme()
  if (theme == 'dark') {
    document.getElementById('themeSlider').checked = true;
  } else {
    document.getElementById('themeSlider').checked = false;
  }
}

//Update the theme in local storage and trigger a theme refresh
function toggleTheme() {
  let theme = readSavedTheme()
  if (theme == 'dark') {
    window.localStorage['theme'] = 'light';
  } else {
    window.localStorage['theme'] = 'dark';
  }
  loadTheme()
}

//Load the theme in local storage
function loadTheme() {
  let theme = readSavedTheme();
  if (theme == 'dark') { //Set theme to dark
    themeSettings.selectedTheme = themeSettings.darkTheme;
  } else { //Set theme to light
    themeSettings.selectedTheme = themeSettings.lightTheme;
  }
  document.body.style.backgroundColor = themeSettings.selectedTheme.backgroundColour;
  document.body.style.color = themeSettings.selectedTheme.textColour;
  applyTheme('graph')
  applyTheme('log')
}
