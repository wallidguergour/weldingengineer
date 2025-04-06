// Sélection du bouton
const copyButton = document.getElementById("copyButton");

// Au clic sur le bouton, on copie le contenu du code
copyButton.addEventListener("click", () => {
  // Récupère le texte à copier
  const codeToCopy = document.getElementById("myCode").innerText;

  // On utilise l'API Clipboard
  navigator.clipboard.writeText(codeToCopy)
    .then(() => {
      alert("Le code a été copié dans le presse-papiers !");
    })
    .catch((err) => {
      console.error("Erreur lors de la copie : ", err);
      alert("Impossible de copier le code. Copiez-le manuellement.");
    });
});
