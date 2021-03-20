$("#menu-toggle").click(function(e) {
  e.preventDefault();
  $("#wrapper").toggleClass("toggled");
});

$("#inner-menu-toggle").click(function(e) {
  e.preventDefault();
  $("#wrapper").toggleClass("toggled");
});

$("#wrapper").toggleClass("toggled");
function reset_animation() {
  var el = document.getElementById('inner-menu-toggle');
  el.style.animation = 'none';
  el.offsetHeight;
  el.style.animation = null;
}
