function cancelReservation(reservationId) {
    if (confirm("Are you sure you want to cancel this reservation?")) {
        alert("No cancellation b#tch!");
    }
}

function rescheduleReservation(reservationId) {
    alert("Rescheduling is currently not implemented."); // Placeholder
}

function handleLogout() {
    if (confirm("Are you sure you want to log out?")) {
        window.location.href = "/logout";
    }
}
