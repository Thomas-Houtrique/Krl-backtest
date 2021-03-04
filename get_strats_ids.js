let strats = Array.prototype.slice.apply(document.querySelectorAll("div.col-sm-12 > app-card-strategy-user:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(2) > div:nth-child(1) > h3:nth-child(1) > a:nth-child(1)"));
strats.forEach((button) => {
    console.log(button.href.split('/')[4]);
   });