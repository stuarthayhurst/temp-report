graphState = 'collapse'
logState = 'collapse'

document.getElementById('logBox').scrollTop = document.getElementById('logBox').scrollHeight

function toggleDropdown(sender, target) {
  if (graphState == 'collapse') {
    if (sender == "arrow") { document.getElementById(target + 'Check').checked = true }
    document.getElementById(target + "Arrow").src=urlRoot + "expand.png";
    graphState = 'expand'
  } else {
    if (sender == "arrow") { document.getElementById(target + 'Check').checked = false }
    document.getElementById(target + "Arrow").src=urlRoot + "collapse.png";
    graphState = 'collapse'
  }
}
