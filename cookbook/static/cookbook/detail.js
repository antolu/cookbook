function uploadRecipe() {
    document.getElementById("upload-recipe").click();
}
$(document).ready(function () {
    $("#sidebar").mCustomScrollbar({
        theme: "minimal"
    });
    $('#dismiss, .overlay').on('click', function () {
        $('#sidebar').removeClass('active');
        $('#sidebarCollapse').toggleClass('active');
        $('#content').toggleClass('active');
        $('#hdr').toggleClass('active');
        $('.collapse.in').toggleClass('in');
        $('.overlay').removeClass('active');
    });
    $('#sidebarCollapse').on('click', function () {
        $('#sidebar').toggleClass('active');
        $('#content').toggleClass('active');
        $('#hdr').toggleClass('active');
      //  $('.collapse.in').toggleClass('in');
        $('a[aria-expanded=true]').attr('aria-expanded', 'false');
        $('#sidebarCollapse').toggleClass('active');
        $('.overlay').toggleClass('active');
    });
});
$(document).ready(function () {
    $(".alert-success").fadeTo(2000, 500).slideUp(500, function () {
        $(".alert-success").slideUp(500);
    });
    $(".alert-danger").fadeTo(2000, 500).slideUp(500, function () {
        $(".alert-danger").slideUp(500);
    });
});
