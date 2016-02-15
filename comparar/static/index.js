/*
 * Entry point runs on page load.
 */
$(function() {
    $('#comparify-btn').on('click', showLoaderAnimation);
});


/*
 * Show the loader animation when submit button is clicked.
 */
function showLoaderAnimation() {
    $('#comparify-btn').hide();
    $('#loading').show();
}
