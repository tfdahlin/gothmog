"use strict";

process.title = 'C2 UI';

const path = require('path');
const express = require('express');
const http = require('http');
const https = require('https');
const app = express();
const favicon = require('serve-favicon');
const fs = require('fs');
const mustache = require('mustache');

const settings = require('./settings');

const template_dir = path.join(__dirname, 'templates');

// Common files
app.use('/css', express.static(path.join(__dirname, 'res', 'css')));
app.use('/media', express.static(path.join(__dirname, 'res', 'media')));
app.use('/javascripts', express.static(path.join(__dirname, 'res', 'javascripts')));

// Favicon
app.use(favicon(path.join(__dirname, 'res', 'favicon', 'favicon.ico')));

function render_template(template_name, context) {
    return new Promise((resolve, reject) => {
        var template_path = path.join(template_dir, template_name);
        if (fs.existsSync(template_path)) {
            var contents = fs.readFileSync(template_path, 'utf-8');
            resolve(mustache.render(contents, context));
        } else {
            reject(`Template ${template_path} not found.`);
        }
    });
}

app.use('/', (req, res) => {
    var context = {
        'site_url': settings['site_url'],
    };
    
    render_template('index.html', context)
    .then((html) => {
        res.status(200).send(html);
    })
    .catch((err) => {
        console.log(err);
        res.status(500).send('Server error.')
    });
});


if(settings['https']) {
    https.createServer({
        key: fs.readFileSync(settings['ssl_key_path']),
        cert: fs.readFileSync(settings['ssl_cert_path']),
        ca: fs.readFileSync(settings['ssl_ca_path'])
    }, app)
    .listen(settings['webPort'], (err) => {
        if (err) {
            return console.log(`Error listening on port ${settings['webPort']}.`)
        }
        console.log(`${new Date()}: HTTPS Web Server is listening on port ${settings['webPort']}.`)
    });
} else {
    app.listen(settings['webPort'], (err) => {
        if (err) {
            return console.log(`Error listening on port ${settings['webPort']}.`)
        }
        console.log(`${new Date()}: HTTP Web Server is listening on port ${settings['webPort']}.`)
    });
}
