// === Form Validation & Confirmation Alerts ===
document.addEventListener("DOMContentLoaded", () => {
  const bookingForm = document.querySelector("form[action='/booking']");
  const contactForm = document.querySelector("form[action='/contact']");

  if (bookingForm) {
    bookingForm.addEventListener("submit", (e) => {
      const name = bookingForm.querySelector("#name").value.trim();
      const email = bookingForm.querySelector("#email").value.trim();
      const checkIn = bookingForm.querySelector("#checkin").value;
      const checkOut = bookingForm.querySelector("#checkout").value;

      if (name.length < 2) {
        e.preventDefault();
        alert("Please enter a valid name (at least 2 characters).");
        return;
      }

      if (!email.includes("@")) {
        e.preventDefault();
        alert("Please enter a valid email address.");
        return;
      }

      if (checkIn === "" || checkOut === "") {
        e.preventDefault();
        alert("Please select both check-in and check-out dates.");
        return;
      }

      // Show confirmation
      alert("Thank you for your booking request, " + name + "! We will contact you shortly.");
    });
  }

  if (contactForm) {
    contactForm.addEventListener("submit", (e) => {
      const name = contactForm.querySelector("#name").value.trim();
      const email = contactForm.querySelector("#email").value.trim();
      const message = contactForm.querySelector("#message").value.trim();

      if (name.length < 2) {
        e.preventDefault();
        alert("Please enter your name.");
        return;
      }

      if (!email.includes("@")) {
        e.preventDefault();
        alert("Please enter a valid email address.");
        return;
      }

      if (message.length < 10) {
        e.preventDefault();
        alert("Message should be at least 10 characters long.");
        return;
      }

      // Show confirmation
      alert("Thank you, " + name + "! Your message has been received.");
    });
  }
});

// === Smooth Scroll to Top on Navbar Brand Click ===
document.querySelector(".navbar-brand")?.addEventListener("click", (e) => {
  e.preventDefault();
  window.scrollTo({ top: 0, behavior: "smooth" });
});
