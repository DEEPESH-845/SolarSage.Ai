/* Runs before paint so reveal targets start hidden instead of flashing in.

   The watchdog matters more than the class: reveal targets are hidden by CSS
   under .js, so if the runtime never arrives the page would stay blank below
   the fold. Four seconds without SS means show everything. */
document.documentElement.className = document.documentElement.className.replace('no-js', 'js');

setTimeout(function () {
  if (!window.SS) document.documentElement.classList.remove('js');
}, 4000);
