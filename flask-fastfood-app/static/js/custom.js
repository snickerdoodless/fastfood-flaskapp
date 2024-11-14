// to get current year
function getYear() {
    var currentDate = new Date();
    var currentYear = currentDate.getFullYear();
    document.querySelector("#displayYear").innerHTML = currentYear;
}

getYear();


// isotope js
$(window).on('load', function () {
    $('.filters_menu li').click(function () {
        $('.filters_menu li').removeClass('active');
        $(this).addClass('active');

        var data = $(this).attr('data-filter');
        $grid.isotope({
            filter: data
        })
    });

    var $grid = $(".grid").isotope({
        itemSelector: ".all",
        percentPosition: false,
        masonry: {
            columnWidth: ".all"
        }
    })
});

// nice select
$(document).ready(function() {
    $('select').niceSelect();
  });

/** google_map js **/
function myMap() {
    var mapProp = {
        center: new google.maps.LatLng(40.712775, -74.005973),
        zoom: 18,
    };
    var map = new google.maps.Map(document.getElementById("googleMap"), mapProp);
}

// client section owl carousel
$(".client_owl-carousel").owlCarousel({
    loop: true,
    margin: 0,
    dots: false,
    nav: true,
    navText: [],
    autoplay: true,
    autoplayHoverPause: true,
    navText: [
        '<i class="fa fa-angle-left" aria-hidden="true"></i>',
        '<i class="fa fa-angle-right" aria-hidden="true"></i>'
    ],
    responsive: {
        0: {
            items: 1
        },
        768: {
            items: 2
        },
        1000: {
            items: 2
        }
    }
});

document.addEventListener('DOMContentLoaded', () => {
    // Flash message handling
    const flashMessages = document.querySelector('.flash-messages'); // Select the flash messages container
    if (flashMessages) {
        const individualMessages = flashMessages.querySelectorAll('.flash-message'); 

        let fadeOutCount = 0; // Counter to keep track of faded out messages

        individualMessages.forEach((flashMessage) => {
            setTimeout(() => {
                flashMessage.style.transition = "opacity 0.5s ease"; // Optional: Add a fade-out effect
                flashMessage.style.opacity = 0; // Fade out
                setTimeout(() => {
                    flashMessage.style.display = 'none'; // Remove from layout
                    fadeOutCount++; // Increment the counter

                    // If all messages have been faded out, hide the parent container
                    if (fadeOutCount === individualMessages.length) {
                        flashMessages.style.display = 'none'; // Hide the entire flash messages container
                    }
                }, 500); // Wait for the fade-out to complete (500ms)
            }, 2000); 
        });
    }
});

function toggleCustomInput() {
    const select = document.getElementById('guest-select');
    const customInputDiv = document.getElementById('custom-guest-input');
    if (select.value === 'custom') {
        customInputDiv.style.display = 'block';
    } else {
        customInputDiv.style.display = 'none';
    }
}

function toggleCustomInput() {
    const select = document.getElementById('guest-select');
    const customInput = document.getElementById('custom-guest-input');
    if (select.value === 'custom') {
        customInput.style.display = 'block';
    } else {
        customInput.style.display = 'none';
    }
}

function validateNumberInput(input) {
    const errorDiv = document.getElementById('custom-input-error');
    const value = parseInt(input.value, 10);
    if (isNaN(value) || value <= 0) {
        errorDiv.style.display = 'block';
    } else {
        errorDiv.style.display = 'none';
    }
}