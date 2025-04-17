document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();

      // Clear loading message
      activitiesList.innerHTML = "";
      // Clear select options except the first one
      activitySelect.length = 1;

      // Populate activities list
      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";
        activityCard.dataset.activityName = name; // Add data attribute for activity name

        const spotsLeft = details.max_participants - details.participants.length;

        // Generate participants list with delete icons
        let participantsHtml = '<div class="participants-list">'; // Use a div instead of ul
        details.participants.forEach((participant) => {
          // Add data attributes for activity name and email
          participantsHtml += `<div class="participant-item">${participant} <span class="delete-icon" data-activity="${name}" data-email="${participant}">🗑️</span></div>`;
        });
        participantsHtml += "</div>";

        activityCard.innerHTML = `
          <h4>${name}</h4>
          <p>${details.description}</p>
          <p><strong>Schedule:</strong> ${details.schedule}</p>
          <p><strong>Availability:</strong> ${spotsLeft} spots left</p>
          <p><strong>Participants:</strong></p>
          ${participantsHtml}
        `;

        activitiesList.appendChild(activityCard);

        // Add option to select dropdown
        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });

      // Add event listeners to delete icons after they are added to the DOM
      addDeleteIconListeners();

    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  // Function to add event listeners to delete icons
  function addDeleteIconListeners() {
    document.querySelectorAll('.delete-icon').forEach(icon => {
      icon.removeEventListener('click', handleUnregisterClick); // Remove existing listener to prevent duplicates
      icon.addEventListener('click', handleUnregisterClick);
    });
  }

  // Handler for delete icon click
  async function handleUnregisterClick(event) {
    const icon = event.target;
    const activityName = icon.dataset.activity;
    const email = icon.dataset.email;

    if (!confirm(`Are you sure you want to unregister ${email} from ${activityName}?`)) {
      return;
    }

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activityName)}/unregister?email=${encodeURIComponent(email)}`,
        {
          method: "DELETE",
        }
      );

      const result = await response.json();

      if (response.ok) {
        // Refresh the activities list to show the updated participant list
        fetchActivities();
        showMessage(result.message, "success");
      } else {
        showMessage(result.detail || "Failed to unregister", "error");
      }
    } catch (error) {
      showMessage("An error occurred during unregistration.", "error");
      console.error("Error unregistering:", error);
    }
  }

  // Function to display messages
  function showMessage(text, type) {
    messageDiv.textContent = text;
    messageDiv.className = `message ${type}`; // Ensure 'message' class is always present
    messageDiv.classList.remove("hidden");

    // Hide message after 5 seconds
    setTimeout(() => {
      messageDiv.classList.add("hidden");
    }, 5000);
  }

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    // Basic validation
    if (!email || !activity) {
        showMessage("Please enter email and select an activity.", "error");
        return;
    }

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        showMessage(result.message, "success");
        signupForm.reset();
        // Refresh activities to show the new participant
        fetchActivities();
      } else {
        showMessage(result.detail || "An error occurred", "error");
      }

    } catch (error) {
      showMessage("Failed to sign up. Please try again.", "error");
      console.error("Error signing up:", error);
    }
  });

  // Initialize app
  fetchActivities();
});
