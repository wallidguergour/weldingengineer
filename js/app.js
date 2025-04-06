new Vue({
  el: '#app',
  data: {
    query: '',
    data: []
  },
  created() {
    fetch('js/pages.json')  // Assurez-vous que le chemin est correct
      .then(response => {
        if (!response.ok) {
          throw new Error('Network response was not ok ' + response.statusText);
        }
        return response.json();
      })
      .then(data => {
        console.log('Data loaded successfully:', data);
        this.data = data;
      })
      .catch(error => console.error('Error loading pages:', error));
  },
  computed: {
    filteredResults() {
      if (this.query.trim() === '') {
        return [];
      }
      return this.data.filter(item => 
        item.title.toLowerCase().includes(this.query.toLowerCase()) || 
        item.description.toLowerCase().includes(this.query.toLowerCase())
      );
    }
  }
});

// Autres composants Vue.js
new Vue({
  el: '#vue',
  data: {
    instagram: '',
    linkedin: 'https://www.linkedin.com/in/wallid-guergour-a12439ba/',
    blogArduino: '',
    blogTOR: '',
    blogHaskell: '',
  }
});

new Vue({
  el: '#Notes1',
  data: {
    StickWelding: "Stick welding consists of a rod of material covered with a flux. The rod is used here as an electrode in the electrical circuit. Melting is achieved by a very high temperature which is obtained by an electric arc between the workpiece and the electrode. The main functions of the electrode coating are to ensure the stability of the arc and to protect the molten metal from the atmosphere. with the gases created during the decomposition of the coating by the heat of the arc. This shielding controls the mechanical properties, chemical composition and metallurgical structure of the weld metal, as well as the characteristics of the electrode."
  }
});

new Vue({
  el: '#Notes2',
  data: {
    WeldBead: "The welding vocabulary is very clear to understand quickly, for the weld bead we use the same words for all welding positions. The two metals to be joined will be called base metals, while the weld bead will be a mixture (molten metal) of these base metals with the filler metal. The base metals can be homogeneous (of the same nature such as steel to steel, copper to copper...) or heterogeneous. Sometimes you may need to weld different types of steel. For example, on buckets fitted to public works machinery, it is possible to build the structure of the part in basic structural steel (S 235) and to reinforce the tooth or blade with much more wear-resistant steels such as hardox 500."
  }
});
