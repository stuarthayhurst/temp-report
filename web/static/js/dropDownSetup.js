graphState = 'collapsed'
logState = 'collapsed'

document.getElementById('logBox').scrollTop = document.getElementById('logBox').scrollHeight

function toggleDropdown(sender, target) {
  if (graphState == 'collapsed') {
    if (sender == "arrow") { document.getElementById(target + 'Check').checked = true }
    document.getElementById(target + "Arrow").src=urlRoot + "expanded.svg";
    graphState = 'expanded'
  } else {
    if (sender == "arrow") { document.getElementById(target + 'Check').checked = false }
    document.getElementById(target + "Arrow").src=urlRoot + "collapsed.svg";
    graphState = 'collapsed'
  }
}
