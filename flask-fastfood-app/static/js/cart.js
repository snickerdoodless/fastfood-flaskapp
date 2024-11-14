function updateQuantity(productId, change) {
  fetch('/cart/update_quantity', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ product_id: productId, change: change }),
  })
  .then(response => response.json())
  .then(data => {
    if (data.error) {
      alert(data.error);
    } else {
      // Update the quantity, item total, and subtotal in the DOM if quantity is above zero
      if (data.quantity > 0) {
        document.getElementById(`quantity-${productId}`).textContent = data.quantity;
        document.getElementById(`price-${productId}`).textContent = `$${data.item_total.toFixed(2)}`;
      } else {
        // Remove item from the DOM if quantity is zero
        const itemElement = document.getElementById(`cart-item-${productId}`);
        if (itemElement) itemElement.remove();
      }

      // Update subtotal and total
      document.getElementById('subtotal').textContent = `$${data.subtotal.toFixed(2)}`;
      document.getElementById('total').textContent = `$${data.total.toFixed(2)}`;

      // Check if the cart is empty
      const cartItems = document.querySelectorAll('.cart-item');
      if (cartItems.length === 0) {
        alert("Your cart is empty. Please add items to proceed.");
        document.getElementById("checkoutBtn").disabled = true; // Disable checkout button
      }
    }
  })
  .catch(error => console.error('Error:', error));
}


function checkCartAndProceed(itemCount) {
  if (!itemCount || itemCount === 0) {
    alert("Your cart is empty. Please add items to proceed.");
  } else {
    location.href = '/checkout';
  }
}

////// Address AJAX
/////

document.getElementById('addressType').addEventListener('change', function() {
  console.log("Address type changed");  // Debugging line to confirm the event is triggered
  loadAddressDetails();
});

function loadAddressDetails() {
  const addressType = document.getElementById("addressType").value;
  
  if (!addressType) {
      console.log("No address type selected");
      return;  // Prevent if no address type is selected
  }

  console.log("Selected address type:", addressType);  // Debugging line to check selected value

  // Make the AJAX request
  fetch(`/checkout/address_details/${addressType}`)
      .then(response => response.json())
      .then(data => {
          if (data.error) {
              alert(data.error); // Display error message if any
          } else {
              console.log("Received address data:", data);  // Debugging line to check the received data
              
              // Adjusted field names based on the specific address type
              const address = data.address;
              if (addressType === 'home') {
                  document.getElementById("streetAddress").value = address.home_street_address || '';
                  document.getElementById("unit").value = address.home_unit || '';
                  document.getElementById("city").value = address.home_city || '';
                  document.getElementById("state").value = address.home_state || '';
                  document.getElementById("postalCode").value = address.home_postal_code || '';
              } else if (addressType === 'office') {
                  document.getElementById("streetAddress").value = address.office_street_address || '';
                  document.getElementById("unit").value = address.office_unit || '';
                  document.getElementById("city").value = address.office_city || '';
                  document.getElementById("state").value = address.office_state || '';
                  document.getElementById("postalCode").value = address.office_postal_code || '';
              }
          }
      })
      .catch(error => {
          console.error("Error fetching address details:", error);
      });
}

///// Payment
////

// Payment Method Tab and Option Management
function changeTabState(selectedTab) {
  const tabs = document.querySelectorAll('.payment-tab');
  tabs.forEach(tab => {
    tab.classList.toggle('bg-red-600', tab.id === selectedTab);
    tab.classList.toggle('text-white', tab.id === selectedTab);
    tab.classList.toggle('bg-gray-100', tab.id !== selectedTab);
    tab.classList.toggle('text-gray-700', tab.id !== selectedTab);
  });
}

// Handle E-Wallet and Card Options Selection
document.querySelectorAll('.payment-option').forEach(option => {
  option.addEventListener('click', function() {
    const parentSection = option.closest('.payment-options');
    
    parentSection.querySelectorAll('.payment-option').forEach(opt => {
      opt.classList.remove('selected', 'border-red-500');
      opt.classList.add('border-transparent');
    });
    
    option.classList.add('selected', 'border-red-500');
    option.classList.remove('border-transparent');
    
    if (option.closest('#ewalletOptions')) {
      const selectedProvider = option.querySelector('img').getAttribute('alt');
      document.getElementById('selectedEwalletProvider').value = selectedProvider;
      console.log("Selected E-Wallet provider:", selectedProvider);
    } else if (option.closest('#cardOptions')) {
      const selectedBank = option.getAttribute('data-bank');
      document.getElementById('selectedBank').value = selectedBank;
      console.log("Selected Bank:", selectedBank);
    }
  });
});

// Payment Method Tab Event Listeners
document.getElementById('ewalletBtn').addEventListener('click', function() {
  document.getElementById('selectedPaymentMethod').value = 'E-Wallet';
  document.getElementById('ewalletOptions').style.display = 'block';
  document.getElementById('cardOptions').style.display = 'none';
  document.querySelectorAll('#cardOptions input').forEach(input => input.value = ''); // Clear card inputs
  changeTabState('ewalletBtn');
});

document.getElementById('debitCardBtn').addEventListener('click', function() {
  document.getElementById('selectedPaymentMethod').value = 'Debit Card';
  document.getElementById('ewalletOptions').style.display = 'none';
  document.getElementById('cardOptions').style.display = 'block';
  document.getElementById('selectedEwalletProvider').value = ''; // Clear e-wallet provider
  document.querySelector('input[name="ewallet_phone"]').value = ''; // Clear e-wallet phone
  changeTabState('debitCardBtn');
});

document.getElementById('creditCardBtn').addEventListener('click', function() {
  document.getElementById('selectedPaymentMethod').value = 'Credit Card';
  document.getElementById('ewalletOptions').style.display = 'none';
  document.getElementById('cardOptions').style.display = 'block';
  document.getElementById('selectedEwalletProvider').value = ''; // Clear e-wallet provider
  document.querySelector('input[name="ewallet_phone"]').value = ''; // Clear e-wallet phone
  changeTabState('creditCardBtn');
});


///// Success
////

// Create confetti animation
function createConfetti() {
  const colors = ['#60A5FA', '#34D399', '#A78BFA', '#F472B6'];
  for (let i = 0; i < 50; i++) {
    const confetti = document.createElement('div');
    confetti.className = 'confetti';
    confetti.style.left = Math.random() * 100 + 'vw';
    confetti.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
    confetti.style.animation = `confettiRain ${1 + Math.random() * 2}s linear forwards`;
    document.body.appendChild(confetti);
    setTimeout(() => confetti.remove(), 3000);
  }
}

// Run confetti animation only on the Order Confirmation page
window.onload = function() {
  if (document.getElementById('order-confirmation-page')) {
    createConfetti();
  }
};


//// Flash MSG
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