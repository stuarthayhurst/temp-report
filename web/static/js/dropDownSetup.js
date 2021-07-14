document.getElementById('logBox').scrollTop = document.getElementById('logBox').scrollHeight

graphState = {
  state: 'collapsed'
}
logState = {
  state: 'collapsed'
}

//Sync with current state
if (document.getElementById('graphCheck').checked == true) {
  graphState.state = 'expanded'
}
if (document.getElementById('logCheck').checked == true) {
  logState.state = 'expanded'
}

function toggleDropdown(sender, target) {
  if (window[target + 'State'].state == 'collapsed') {
    if (sender == "arrow") { document.getElementById(target + 'Check').checked = true }
    document.getElementById(target + "Arrow").src=urlRoot + "expanded.svg";
    window[target + 'State'].state = 'expanded'
  } else {
    if (sender == "arrow") { document.getElementById(target + 'Check').checked = false }
    document.getElementById(target + "Arrow").src=urlRoot + "collapsed.svg";
    window[target + 'State'].state = 'collapsed'
  }
}
