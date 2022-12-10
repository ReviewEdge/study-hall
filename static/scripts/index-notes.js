(() => {
  let notesDiv
  let sortByEl
  let sortDirEl
  let notes = []

  window.addEventListener("DOMContentLoaded", async () => {
    notesDiv = document.getElementById("notes")
    sortByEl = document.getElementById("sort-by")
    sortDirEl = document.getElementById("sort-dir")

    notes = [].slice.call(notesDiv.children)
    
    if (notes.length > 0) {
      sortByEl.addEventListener("change", sortNotes)
      sortDirEl.addEventListener("change", sortNotes)
    }
  })

  const sortNotes = () => {
    const sortBy = sortByEl.value
    const sortDir = sortDirEl.value

    notes = notes.sort((a,b) => {
      if (sortBy === "title") {
        if (sortDir === "asc") {
          return a.dataset[sortBy].localeCompare(b.dataset[sortBy], undefined, {sensitivity: 'base'})
        } else {
          return b.dataset[sortBy].localeCompare(a.dataset[sortBy], undefined, {sensitivity: 'base'})
        }
      }
      const aDate = new Date(a.dataset[sortBy])
      const bDate = new Date(b.dataset[sortBy])
      return sortDir === "asc" ? aDate - bDate : bDate - aDate
    })

    notesDiv.innerHTML = ""
    for (const note of notes) {
      notesDiv.appendChild(note)
    }
  }
})()
