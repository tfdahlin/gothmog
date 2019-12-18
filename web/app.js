#!/usr/bin/env node
// -*- coding: utf-8 -*-
// Filename: web/app.js
"use strict";

// Native imports
const fs = require('fs');
const http = require('http');
const https = require('https');
const path = require('path');

// NPM imports
const express = require('express');
const favicon = require('serve-favicon');
const mustache = require('mustache');

// Local imports
const settings = require('./settings');

process.title = 'C2 Web UI';
const template_dir = path.join(__dirname, 'templates');
const javascripts_dir = path.join(__dirname, 'res', 'javascripts');
const app = express();

// Functions
function render_template(template_name, context) {
    /*Render a specific template with a given context.

    Arguments:
        template_name (string): Name of the file within the template directory to render.
        context (object): Context information for rendering within the template.
    */
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

function start_server(app) {
    /*Create and start the server for the Gothmog web UI.

    Arguments:
        app (express): The express app to use for the server.
    */
    var server = null;
    if(settings['https']) {
        server = https.createServer({
            key: fs.readFileSync(settings['ssl_key_path']),
            cert: fs.readFileSync(settings['ssl_cert_path']),
            ca: fs.readFileSync(settings['ssl_ca_path'])
        }, app);
    } else {
        server = app;
    }
    server.listen(settings['webPort'], (err) => {
        if (err) {
            return console.log(`Error listening on port ${settings['webPort']}.`);
        }
        console.log(`${new Date()}: Web Server is listening on port ${settings['webPort']}.`);
    }).on('error', (err) => {
        if (err['code'] == 'EADDRINUSE') {
            console.log(`Port ${err['port']} is already in use on this machine, so the Gothmog web UI cannot launch.\n`);  
            console.log(`In order to proceed, please either change the settings to a different port,`)
            console.log(`or close the existing application on port ${err['port']}.`);
        } else {
            throw err;
        }
    });
}

function fetch_file_contents(filename) {
    /*Read a given file and resolves its contents.

    Arguments:
        filename (string): The file to be opened and read.
    */
    return new Promise((resolve, reject) => {
        fs.readFile(filename, 'utf-8', function (err, contents) {
            if (err) {
                console.log(err);
                reject('Could not read file: ' + filename);
            } else {
                resolve(contents);
            }
        });
    });
}

function fetch_static_javascript(filename) {
    /*Fetch a javascript file from res/javascripts from the allowed files, else rejects.

    Arguments:
        filename (string): The file to be fetched, if it is an existing file.
    */
    return new Promise((resolve, reject) => {
        var valid_files = [
            'main.js'
        ];
        // if the given file is a valid one
        if (valid_files.indexOf(filename) >= 0) {
            fetch_file_contents(path.join(javascripts_dir, filename))
            .then((contents) => {
                resolve(contents);
            })
            .catch((err) => {
                reject(err);
            });
        }
    });
}

function render_static_javascript(filename, context) {
    /*Fetch a javascript file and render it with a given context.

    Arguments:
        filename (string): The filename to be fetched from res/javascripts for rendering.
        context (object): Context to be included in the rendering process.
    */
    return new Promise((resolve, reject) => {
        fetch_static_javascript(filename)
        .then((html) => {
            resolve(mustache.render(html, context));
        })
        .catch((err) => {
            reject(err);
        });
    });
}

// Common files
app.use('/css', express.static(path.join(__dirname, 'res', 'css')));
app.use('/media', express.static(path.join(__dirname, 'res', 'media')));

// Favicon
app.use(favicon(path.join(__dirname, 'res', 'favicon', 'favicon.ico')));

// Routes
app.use('/javascripts/:filename', (req, res) => {
    /*

    */
    var context = {
        'api_url': settings['api_url'],
    };
    render_static_javascript(req.params['filename'], context)
    .then((javascript) => {
        res.status(200).type('application/json').send(javascript);
    })
    .catch((err) => {
        console.log(err);
        res.status(500).send('Server error.');
    });
});

app.use('/', (req, res) => {
    /*

    */
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

start_server(app);
