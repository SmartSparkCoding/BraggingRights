document.addEventListener("DOMContentLoaded", () => {
  initialiseAdmin();
});

function initialiseAdmin() {
  setupModalControls();
  setupGameControls();
  setupCompetitionControls();
  setupDangerZone();
}

function setupModalControls() {
  document.querySelectorAll("[data-open-modal]").forEach((button) => {
    button.addEventListener("click", () => {
      const modal = document.getElementById(button.dataset.openModal);

      if (!modal) {
        return;
      }

      modal.classList.add("open");
      document.body.classList.add("modal-open");
    });
  });

  document.querySelectorAll("[data-close-modal]").forEach((button) => {
    button.addEventListener("click", () => {
      closeModal(button.closest(".modal"));
    });
  });

  document.querySelectorAll(".modal").forEach((modal) => {
    modal.addEventListener("click", (event) => {
      if (event.target === modal) {
        closeModal(modal);
      }
    });
  });

  document.addEventListener("keydown", (event) => {
    if (event.key !== "Escape") {
      return;
    }

    const openModal = document.querySelector(".modal.open");

    if (openModal) {
      closeModal(openModal);
    }
  });
}

function closeModal(modal) {
  if (!modal) {
    return;
  }

  modal.classList.remove("open");

  if (!document.querySelector(".modal.open")) {
    document.body.classList.remove("modal-open");
  }
}

function openModal(modalId) {
  const modal = document.getElementById(modalId);

  if (!modal) {
    return;
  }

  modal.classList.add("open");
  document.body.classList.add("modal-open");
}

function setupGameControls() {
  const addGameForm = document.getElementById("add-game-form");

  if (addGameForm) {
    addGameForm.addEventListener("submit", async (event) => {
      event.preventDefault();

      const submitButton = addGameForm.querySelector('button[type="submit"]');

      const originalText = submitButton ? submitButton.textContent : "";

      if (submitButton) {
        submitButton.disabled = true;
        submitButton.textContent = "Adding...";
      }

      const formData = new FormData(addGameForm);

      try {
        const response = await fetch("/admin/api/games", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            name: formData.get("name"),
            description: formData.get("description"),
          }),
        });

        const result = await response.json();

        if (!response.ok) {
          throw new Error(result.error || "Failed to add game.");
        }

        showNotification("Game added successfully.", "success");

        addGameForm.reset();

        closeModal(addGameForm.closest(".modal"));

        setTimeout(() => {
          window.location.reload();
        }, 500);
      } catch (error) {
        showNotification(error.message, "error");
      } finally {
        if (submitButton) {
          submitButton.disabled = false;
          submitButton.textContent = originalText;
        }
      }
    });
  }

  document.querySelectorAll("[data-edit-game]").forEach((button) => {
    button.addEventListener("click", () => {
      document.getElementById("edit-game-id").value = button.dataset.editGame;

      document.getElementById("edit-game-name").value =
        button.dataset.gameName || "";

      document.getElementById("edit-game-description").value =
        button.dataset.gameDescription || "";

      openModal("edit-game-modal");
    });
  });

  const editGameForm = document.getElementById("edit-game-form");

  if (editGameForm) {
    editGameForm.addEventListener("submit", async (event) => {
      event.preventDefault();

      const gameId = document.getElementById("edit-game-id").value;

      const submitButton = editGameForm.querySelector('button[type="submit"]');

      const originalText = submitButton ? submitButton.textContent : "";

      if (submitButton) {
        submitButton.disabled = true;
        submitButton.textContent = "Saving...";
      }

      try {
        const response = await fetch(`/admin/api/games/${gameId}`, {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            name: document.getElementById("edit-game-name").value.trim(),
            description: document
              .getElementById("edit-game-description")
              .value.trim(),
          }),
        });

        const result = await response.json();

        if (!response.ok) {
          throw new Error(result.error || "Failed to update game.");
        }

        showNotification("Game updated successfully.", "success");

        closeModal(editGameForm.closest(".modal"));

        setTimeout(() => {
          window.location.reload();
        }, 500);
      } catch (error) {
        showNotification(error.message, "error");
      } finally {
        if (submitButton) {
          submitButton.disabled = false;
          submitButton.textContent = originalText;
        }
      }
    });
  }

  document.querySelectorAll("[data-delete-game]").forEach((button) => {
    button.addEventListener("click", async () => {
      const gameId = button.dataset.deleteGame;

      const gameName = button.dataset.gameName || "this game";

      const confirmed = confirm(
        `Are you sure you want to delete "${gameName}"?`,
      );

      if (!confirmed) {
        return;
      }

      try {
        const response = await fetch(`/admin/api/games/${gameId}`, {
          method: "DELETE",
        });

        const result = await response.json();

        if (!response.ok) {
          throw new Error(result.error || "Failed to delete game.");
        }

        showNotification("Game deleted successfully.", "success");

        setTimeout(() => {
          window.location.reload();
        }, 500);
      } catch (error) {
        showNotification(error.message, "error");
      }
    });
  });
}

function setupCompetitionControls() {
  const form = document.getElementById("add-competition-form");

  const modalTitle = document.getElementById("competition-modal-title");

  const modalDescription = document.getElementById(
    "competition-modal-description",
  );

  const competitionId = document.getElementById("competition-id");

  const submitButton = form
    ? form.querySelector('button[type="submit"]')
    : null;

  document.querySelectorAll("[data-manage-competition]").forEach((button) => {
    button.addEventListener("click", async () => {
      const id = button.dataset.manageCompetition;

      try {
        const response = await fetch(`/admin/api/competitions/${id}`);

        const result = await response.json();

        if (!response.ok) {
          throw new Error(result.error || "Failed to load competition.");
        }

        const competition = result.competition;

        const goals = result.goals || [];

        const bigGoal = goals.find((goal) => goal.goal_type === "big") || {};

        const smallGoals = goals.filter((goal) => goal.goal_type === "small");

        competitionId.value = competition.id;

        document.getElementById("competition-name").value =
          competition.name || "";

        document.getElementById("competition-start").value =
          competition.start_date || "";

        document.getElementById("competition-end").value =
          competition.end_date || "";

        document.getElementById("big-goal-name").value = bigGoal.name || "";

        document.getElementById("big-goal-game").value =
          bigGoal.game_type_id || "";

        document.getElementById("big-goal-prize").value = bigGoal.prize || "";

        const firstSmallGoal = smallGoals[0] || {};

        const secondSmallGoal = smallGoals[1] || {};

        document.getElementById("small-goal-1-name").value =
          firstSmallGoal.name || "";

        document.getElementById("small-goal-1-game").value =
          firstSmallGoal.game_type_id || "";

        document.getElementById("small-goal-1-prize").value =
          firstSmallGoal.prize || "";

        document.getElementById("small-goal-2-name").value =
          secondSmallGoal.name || "";

        document.getElementById("small-goal-2-game").value =
          secondSmallGoal.game_type_id || "";

        document.getElementById("small-goal-2-prize").value =
          secondSmallGoal.prize || "";

        modalTitle.textContent = "Manage Competition";

        modalDescription.textContent =
          "Update dates, goals and prizes for this competition.";

        if (submitButton) {
          submitButton.textContent = "Save Competition";
        }

        openModal("add-competition-modal");
      } catch (error) {
        showNotification(error.message, "error");
      }
    });
  });

  if (form) {
    form.addEventListener("submit", async (event) => {
      event.preventDefault();

      const id = competitionId.value;

      const isEditing = Boolean(id);

      const originalText = submitButton ? submitButton.textContent : "";

      if (submitButton) {
        submitButton.disabled = true;
        submitButton.textContent = isEditing ? "Saving..." : "Creating...";
      }

      const data = {
        name: document.getElementById("competition-name").value.trim(),

        start_date: document.getElementById("competition-start").value,

        end_date: document.getElementById("competition-end").value,

        big_goal: {
          name: document.getElementById("big-goal-name").value,

          prize: document.getElementById("big-goal-prize").value.trim(),

          game_type_id: document.getElementById("big-goal-game").value || null,
        },

        small_goals: [
          {
            name: document.getElementById("small-goal-1-name").value,

            prize: document.getElementById("small-goal-1-prize").value.trim(),

            game_type_id:
              document.getElementById("small-goal-1-game").value || null,
          },
          {
            name: document.getElementById("small-goal-2-name").value,

            prize: document.getElementById("small-goal-2-prize").value.trim(),

            game_type_id:
              document.getElementById("small-goal-2-game").value || null,
          },
        ],
      };

      try {
        const response = await fetch(
          isEditing
            ? `/admin/api/competitions/${id}`
            : "/admin/api/competitions",
          {
            method: isEditing ? "PUT" : "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify(data),
          },
        );

        const result = await response.json();

        if (!response.ok) {
          throw new Error(result.error || "Failed to save competition.");
        }

        showNotification(
          isEditing
            ? "Competition updated successfully."
            : "Competition created successfully.",
          "success",
        );

        form.reset();

        competitionId.value = "";

        modalTitle.textContent = "New Competition";

        modalDescription.textContent =
          "Create a competition with one big goal and two smaller goals.";

        if (submitButton) {
          submitButton.textContent = "Create Competition";
        }

        closeModal(form.closest(".modal"));

        setTimeout(() => {
          window.location.reload();
        }, 500);
      } catch (error) {
        showNotification(error.message, "error");
      } finally {
        if (submitButton) {
          submitButton.disabled = false;

          if (
            submitButton.textContent === "Saving..." ||
            submitButton.textContent === "Creating..."
          ) {
            submitButton.textContent = originalText;
          }
        }
      }
    });
  }

  document.querySelectorAll("[data-delete-competition]").forEach((button) => {
    button.addEventListener("click", async () => {
      const competitionId = button.dataset.deleteCompetition;

      const competitionName =
        button.dataset.competitionName || "this competition";

      const confirmed = confirm(
        `Are you sure you want to delete "${competitionName}"?`,
      );

      if (!confirmed) {
        return;
      }

      try {
        const response = await fetch(
          `/admin/api/competitions/${competitionId}`,
          {
            method: "DELETE",
          },
        );

        const result = await response.json();

        if (!response.ok) {
          throw new Error(result.error || "Failed to delete competition.");
        }

        showNotification("Competition deleted successfully.", "success");

        setTimeout(() => {
          window.location.reload();
        }, 500);
      } catch (error) {
        showNotification(error.message, "error");
      }
    });
  });
}

function setupDangerZone() {
  const clearGamesButton = document.querySelector("[data-clear-games]");

  if (clearGamesButton) {
    clearGamesButton.addEventListener("click", async () => {
      const confirmed = confirm(
        "This will permanently delete every recorded game and all associated player results. Are you sure?",
      );

      if (!confirmed) {
        return;
      }

      const secondConfirmation = confirm(
        "This action cannot be undone. Continue?",
      );

      if (!secondConfirmation) {
        return;
      }

      try {
        const response = await fetch("/admin/api/games/clear", {
          method: "DELETE",
        });

        const result = await response.json();

        if (!response.ok) {
          throw new Error(result.error || "Failed to clear games.");
        }

        showNotification("All recorded games have been deleted.", "success");

        setTimeout(() => {
          window.location.reload();
        }, 700);
      } catch (error) {
        showNotification(error.message, "error");
      }
    });
  }

  const resetDatabaseButton = document.querySelector("[data-reset-database]");

  if (resetDatabaseButton) {
    resetDatabaseButton.addEventListener("click", async () => {
      const confirmed = confirm(
        "WARNING: This will permanently delete ALL Bragging Rights data, including games, competitions and game types. Are you absolutely sure?",
      );

      if (!confirmed) {
        return;
      }

      const secondConfirmation = prompt(
        'Type "RESET" to permanently reset the database.',
      );

      if (secondConfirmation !== "RESET") {
        showNotification("Database reset cancelled.", "error");

        return;
      }

      try {
        const response = await fetch("/admin/api/database/reset", {
          method: "POST",
        });

        const result = await response.json();

        if (!response.ok) {
          throw new Error(result.error || "Failed to reset database.");
        }

        showNotification("Database reset successfully.", "success");

        setTimeout(() => {
          window.location.reload();
        }, 700);
      } catch (error) {
        showNotification(error.message, "error");
      }
    });
  }
}

function showNotification(message, type = "success") {
  let container = document.getElementById("notification-container");

  if (!container) {
    container = document.createElement("div");

    container.id = "notification-container";

    document.body.appendChild(container);
  }

  const notification = document.createElement("div");

  notification.className = `admin-notification ${type}`;

  notification.textContent = message;

  container.appendChild(notification);

  requestAnimationFrame(() => {
    notification.classList.add("visible");
  });

  setTimeout(() => {
    notification.classList.remove("visible");

    setTimeout(() => {
      notification.remove();
    }, 300);
  }, 3500);
}
