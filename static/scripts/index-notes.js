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

    const sortByAttr = sortBy === "updated" ? "updatedAt" : "createdAt"
    notes = notes.sort((a,b) => {
      const aDate = new Date(a.dataset[sortByAttr])
      const bDate = new Date(b.dataset[sortByAttr])
      return sortDir === "asc" ? aDate - bDate : bDate - aDate
    })

    notesDiv.innerHTML = ""
    for (const note of notes) {
      notesDiv.appendChild(note)
    }
  }
})()
