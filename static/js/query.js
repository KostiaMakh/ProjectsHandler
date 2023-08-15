function getQuery(token) {
     let sql_query = document.getElementById('sqlRequest')
    $.ajax({
        type: "POST",
        url: "/raw-sql-query/",
        data: {
            "csrfmiddlewaretoken": `${token}`,
            code: sql_query,
        },
        success: function (response) {
            console.log('YES')

        },
        error: function (response) {
            console.log('NO')
        },
    });

}