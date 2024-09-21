document.addEventListener('DOMContentLoaded', function () {
    const courseField = document.getElementById('id_course');
    const profDispoField = document.getElementById('id_prof_dispo');

    // Fonction pour mettre à jour les plages horaires via AJAX
    function updateProfDispoOptions(courseId) {
        if (!courseId) {
            profDispoField.innerHTML = '';  // Vide les options
            return;
        }

        // Requête AJAX pour obtenir les plages horaires du professeur du cours sélectionné
        const xhr = new XMLHttpRequest();
        xhr.open('GET', `/admin/get_prof_dispo/?course_id=${courseId}`, true);
        xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
        xhr.onload = function () {
            if (xhr.status >= 200 && xhr.status < 400) {
                const response = JSON.parse(xhr.responseText);
                profDispoField.innerHTML = '';  // Vide le champ actuel
                response.forEach(function (option) {
                    const newOption = document.createElement('option');
                    newOption.value = option.id;
                    newOption.text = option.text;
                    profDispoField.appendChild(newOption);
                });
            }
        };
        xhr.send();
    }

    // Écoute le changement du champ `course`
    courseField.addEventListener('change', function () {
        const courseId = this.value;
        updateProfDispoOptions(courseId);
    });

    // Mise à jour initiale si un cours est déjà sélectionné lors du chargement
    if (courseField.value) {
        updateProfDispoOptions(courseField.value);
    }
});
