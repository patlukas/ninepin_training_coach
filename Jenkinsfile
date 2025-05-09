pipeline {
    agent any
    environment {
        BRANCH = 'master'
        GITHUB_USER = "patlukas"
        REPO_NAME = "ninepin_training_coach"
        FILES = '["config.json"]'
    }
    stages {
        stage('Checkout') {
            steps {
                   git branch: "${BRANCH}", url: "https://github.com/${GITHUB_USER}/${REPO_NAME}.git", credentialsId: 'github-token'
            }
        }
        stage('Extract Version and Name from main.py') {
            steps {
                script {
                    env.APP_VERSION = (readFile("main.py") =~ /APP_VERSION\s*=\s*"(.*)"/)[0][1]
                    env.APP_NAME = (readFile("main.py") =~ /APP_NAME\s*=\s*"(.*)"/)[0][1]
                    env.EXE_NAME_PREFIX = (readFile("main.py") =~ /EXE_NAME\s*=\s*"(.*)"/)[0][1]
                    echo "From 'main.py'\tAPP_NAME: ${env.APP_NAME}\tAPP_VERSION: ${env.APP_VERSION}"
                }
            }
        }
        stage('Get last release from github') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'github-token', usernameVariable: 'GITHUB_USER', passwordVariable: 'GITHUB_TOKEN')]) {
                    script {
                        def response = bat(
                            script: """ @curl -s -k -H "Authorization: token %GITHUB_TOKEN%" "https://api.github.com/repos/${GITHUB_USER}/${REPO_NAME}/releases/latest" """,
                            returnStdout: true
                        ).trim()
                        def json = readJSON text: response
                        if (json.name) {
                            env.LATEST_RELEASE = json.name
                            echo "Last release: ${env.LATEST_RELEASE}"
                        } else {
                            env.LATEST_RELEASE = "v0.0.0"
                            error "Nie udaÅ‚o siÄ™ pobraÄ‡ informacji o release!"
                        }
                    }
                }
            }
        }
        stage('Determining the name of the next release') {
            steps {
                script {
                    def vLast = env.LATEST_RELEASE.replaceAll("^v", "").split("\\.")
                    def vNext = env.APP_VERSION.split("\\.")

                    if (vLast[0] == vNext[0] && vLast[1] == vNext[1] && vLast[2] == vNext[2]) {
                        if (vLast.size() > 3 && vLast[3].isNumber()) {
                            env.APP_VERSION = env.APP_VERSION + "." + (vLast[3].toInteger() + 1)
                        } else {
                            env.APP_VERSION = env.APP_VERSION + ".1"
                        }
                    } else {
                        env.APP_VERSION = env.APP_VERSION + ".0"
                    }
                    echo "Next release: ${env.APP_VERSION}"
                }
            }
        }
        stage('Determining file name') {
            steps {
                script {
                    env.FILE_NAME = env.APP_NAME + "_" + env.APP_VERSION.replace(".", "_")
                    env.ZIP_NAME = "${env.FILE_NAME}.zip"
                    env.EXE_NAME = "${env.EXE_NAME_PREFIX}_${env.APP_VERSION.replace(".", "_")}.exe"
                    echo "Zip path: ${env.ZIP_NAME}\tExe path: ${env.EXE_NAME}"
                }
            }
        }
        stage('Build EXE') {
            steps {
                bat '''
                "%PYTHON34%\\Scripts\\pyinstaller.exe" --distpath . --onefile --icon=icon/icon.ico --noconsole --name "%EXE_NAME%" main.py
                '''
            }
        }
        stage('Create ZIP') {
            steps {
                script {
                    def filesToAdd = new groovy.json.JsonSlurper().parseText(env.FILES)
                    filesToAdd.add(env.EXE_NAME)

                    zip(
                        zipFile: env.ZIP_NAME,
                        dir: "",
                        archive: false,
                        overwrite: true,
                        glob: filesToAdd.join(",")
                    )
                    echo "Zip was created: ${env.ZIP_NAME}"
                }
            }
        }
        stage('Create Tag') {
            steps {
            withCredentials([
                    gitUsernamePassword(credentialsId: 'github-token', gitToolName: 'Default')
                ]) {
                    script {
                        env.TAG_NAME = "v" + env.APP_VERSION
                        def commitHash = bat(script: "@git rev-parse HEAD", returnStdout: true).trim()

                        bat """
                            git tag ${env.TAG_NAME} ${commitHash}
                            git push origin ${env.TAG_NAME}
                        """
                        echo "New tag: ${env.TAG_NAME}"
                    }
                }
            }
        }
        stage('Create Release on GitHub') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'github-token', usernameVariable: 'GITHUB_USER', passwordVariable: 'GITHUB_TOKEN')]) {
                    script {
                        def body = "New release"
                        if (fileExists('about_release.txt')) {
                            body = readFile('about_release.txt')
                            body = body.replaceAll('"', "'")
                        }

                        def releaseData = [
                            "tag_name": env.TAG_NAME,
                            "name": env.TAG_NAME,
                            "body": "${body}",
                            "draft": false,
                            "prerelease": false,
                            "generate_release_notes":false
                        ]

                        def releaseJson = groovy.json.JsonOutput.toJson(releaseData).replace('"', '\\"')
                         def releaseResponse = bat(script: """
                            @curl -k -L -X POST -H \"Authorization: Bearer %GITHUB_TOKEN%\" -H \"Accept: application/vnd.github+json\" ^
                            -H \"X-GitHub-Api-Version: 2022-11-28\" -d "${releaseJson}" "https://api.github.com/repos/${GITHUB_USER}/${REPO_NAME}/releases"
                        """, returnStdout: true).trim()
                        def releaseInfo = readJSON text: releaseResponse
                        def releaseId = releaseInfo.id
                        if (fileExists(env.ZIP_NAME)) {
                            def uploadUrl = "https://uploads.github.com/repos/${GITHUB_USER}/${REPO_NAME}/releases/${releaseId}/assets?name=${env.ZIP_NAME}"
                            bat """
                                curl -k -X POST -H "Authorization: token %GITHUB_TOKEN%" -H "Content-Type: application/octet-stream" ^
                                --data-binary @\"${env.ZIP_NAME}\" \"${uploadUrl}\"
                            """
                            echo "Add file ${env.ZIP_NAME} to release."
                        } else {
                            echo "File ${env.ZIP_NAME} not exists."
                        }
                    }
                }
            }
        }
        stage('Del files') {
            steps {
                script {
                    echo "DEL"
                    bat """
                        del /f /q *
                        for /d %%i in (*) do rmdir /s /q "%%i"
                        rmdir /s /q .git
                    """
                }
            }
        }
    }

}