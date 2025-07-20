document.addEventListener("DOMContentLoaded", () => {
  // === Hero Carousel ===
  const slides = document.querySelectorAll(".hero-slide");
  let currentSlide = 0;

  if (slides.length > 1) {
    setInterval(() => {
      slides[currentSlide].classList.remove("opacity-100", "z-10");
      slides[currentSlide].classList.add("opacity-0", "z-0");

      currentSlide = (currentSlide + 1) % slides.length;

      slides[currentSlide].classList.remove("opacity-0", "z-0");
      slides[currentSlide].classList.add("opacity-100", "z-10");
    }, 5000);
  }

  // === Booking Form Validation ===
  const bookingForm = document.querySelector("form[action='/booking']");
  if (bookingForm) {
    bookingForm.addEventListener("submit", (e) => {
      const name = bookingForm.querySelector("#name")?.value.trim();
      const email = bookingForm.querySelector("#email")?.value.trim();
      const checkIn = bookingForm.querySelector("#checkin")?.value;
      const checkOut = bookingForm.querySelector("#checkout")?.value;

      if (!name || name.length < 2) {
        e.preventDefault();
        showToast("Please enter a valid name (at least 2 characters).", "bg-red-500");
        return;
      }

      if (!email || !email.includes("@")) {
        e.preventDefault();
        showToast("Please enter a valid email address.", "bg-red-500");
        return;
      }

      if (!checkIn || !checkOut) {
        e.preventDefault();
        showToast("Please select both check-in and check-out dates.", "bg-red-500");
        return;
      }

      showToast(`Thank you for your booking request, ${name}! We will contact you shortly.`, "bg-green-500");
    });
  }

  // === Contact Form Validation ===
  const contactForm = document.querySelector("form[action='/contact']");
  if (contactForm) {
    contactForm.addEventListener("submit", (e) => {
      const name = contactForm.querySelector("#name")?.value.trim();
      const email = contactForm.querySelector("#email")?.value.trim();
      const message = contactForm.querySelector("#message")?.value.trim();

      if (!name || name.length < 2) {
        e.preventDefault();
        showToast("Please enter your name.", "bg-red-500");
        return;
      }

      if (!email || !email.includes("@")) {
        e.preventDefault();
        showToast("Please enter a valid email address.", "bg-red-500");
        return;
      }

      if (!message || message.length < 10) {
        e.preventDefault();
        showToast("Message should be at least 10 characters long.", "bg-red-500");
        return;
      }

      showToast(`Thank you, ${name}! Your message has been received.`, "bg-green-500");
    });
  }

  // === Smooth Scroll to Top on Brand Click ===
  const brandLink = document.querySelector(".navbar-brand");
  if (brandLink) {
    brandLink.addEventListener("click", (e) => {
      e.preventDefault();
      window.scrollTo({ top: 0, behavior: "smooth" });
    });
  }

  // === Invoice Download Modal Animation with Success Popup ===
  const downloadBtn = document.getElementById("download-invoice-btn");
  const modal = document.getElementById("downloadModal");
  const closeModalBtn = document.getElementById("closeModalBtn");
  const successModal = document.getElementById("downloadSuccessModal");
  const closeSuccessBtn = document.getElementById("closeSuccessBtn");

  if (downloadBtn && modal) {
    downloadBtn.addEventListener("click", () => {
      modal.classList.remove("hidden");

      const bookingId = downloadBtn.dataset.bookingId;
      if (bookingId) {
        fetch(`/invoice/${bookingId}`)
          .then(res => res.blob())
          .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            a.download = `Kasvi_Invoice_${bookingId}.pdf`;
            document.body.appendChild(a);
            a.click();
            a.remove();
            window.URL.revokeObjectURL(url);
          })
          .catch(err => {
            showToast("Failed to download invoice.", "bg-red-500");
            console.error(err);
          });
      }

      setTimeout(() => {
        modal.classList.add("hidden");
        if (successModal) {
          successModal.classList.remove("hidden");
          setTimeout(() => {
            successModal.classList.add("hidden");
          }, 4000);
        }
      }, 3000);
    });
  }

  if (closeModalBtn) {
    closeModalBtn.addEventListener("click", () => {
      modal.classList.add("hidden");
    });
  }

  if (closeSuccessBtn) {
    closeSuccessBtn.addEventListener("click", () => {
      successModal.classList.add("hidden");
    });
  }
});

// ✅ Toast Function
function showToast(message, color = 'bg-red-500') {
  const toast = document.getElementById("toast");
  const toastMessage = document.getElementById("toast-message");

  if (!toast || !toastMessage) return;

  toast.classList.remove("bg-red-500", "bg-green-500", "bg-blue-500");
  toast.classList.add(color);
  toastMessage.textContent = message;
  toast.classList.remove("hidden");

  setTimeout(() => {
    toast.classList.add("hidden");
  }, 4000);
}
