(() => {
  window.addEventListener("DOMContentLoaded", async () => {
    const deleteBtn = document.getElementById("delete-account")
    deleteBtn.addEventListener("click", deleteAccount)
  })

  const deleteAccount = () => {
    if (confirm("Are you sure? This action cannot be undone.")) {
      fetch(`/api/account`, {method: 'DELETE'})
        .then(() => {
          // redirect to the index page
          window.location.href = '/'
        })
        .catch(error => console.log(error))
    }
  }
})()
