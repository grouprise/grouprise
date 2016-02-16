module.exports = function (grunt) {
    var pkg = grunt.file.readJSON("package.json");

    // static files
    var raw_banner = grunt.file.read("res/templates/banner.txt");
    var banner = grunt.template.process(raw_banner, { data: { package: pkg } });

    // postcss config
    var postcss_autoprefixer = require("autoprefixer")({browsers: ["last 5 versions", "ie 11"]});
    var postcss_banner = require("postcss-banner")({ banner: banner });
    var postcss_wring = require("csswring");

    // Project configuration.
    grunt.initConfig({
        less: {
            options: {
                strictMath: true,
                strictUnits: true,
                sourceMap: true,
                outputSourceFiles: true,
                compress: false
            },
            app: {
                options: {
                    sourceMapFilename: "build/css/app_unprefixed.css.map",
                    sourceMapURL: "./app_unprefixed.css.map"
                },
                files: {
                    "build/css/app_unprefixed.css": "res/less/app.less"
                }
            }
        },
        postcss: {
            options: {
                map: {
                    inline: false,
                    annotation: true,
                    prev: "build/css/app.css.map"
                },
                processors: [
                    postcss_autoprefixer,
                    postcss_wring,
                    postcss_banner
                ]
            },
            dist: {
                src: "build/css/app_unprefixed.css",
                dest: "media/css/app.css"
            }
        },
        watch: {
            less: {
                files: ["res/**/*.less"],
                tasks: ["css"]
            },
        }
    });

    // These plugins provide necessary tasks.
    grunt.loadNpmTasks("grunt-contrib-less");
    grunt.loadNpmTasks("grunt-contrib-watch");
    grunt.loadNpmTasks("grunt-postcss");

    // Default task.
    grunt.registerTask("css", ["less", "postcss"]);
    grunt.registerTask("default", ["css"]);
};
