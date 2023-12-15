document.getElementById('contentHider').onclick = hideFilterBl;
let a = document.getElementById('id_order_by');
a.classList.add('form-control');
a.classList.add('mb-3');

function hideFilterBl() {
    let filtersDetails = document.getElementById('filters');
    let content_hider = document.getElementById('contentHider');
    let chevron = document.getElementById('chevron');
    filtersDetails.style.width = 0;
    filtersDetails.style.paddingLeft = 0;
    filtersDetails.style.paddingRight = 0;
    content_hider.style.opacity = 0;
    content_hider.style.display = 'none'

}

function showFilters() {
    let filtersDetails = document.getElementById('filters');
    let content_hider = document.getElementById('contentHider');
    let chevron = document.getElementById('chevron');

    if (content_hider.style.display === 'none') {
        content_hider.style.display = 'block'
        setTimeout(() => {
            content_hider.style.display = 'block'
            content_hider.style.opacity = 0.7;
            content_hider.style.transition = "opacity 300ms";
        }, 400)

        filtersDetails.style.width = '350px';
        filtersDetails.style.paddingLeft = '20px';
        filtersDetails.style.paddingRight = '20px';
        filtersDetails.style.transition = "all 430ms";

    } else {
        hideFilterBl()
    }

}