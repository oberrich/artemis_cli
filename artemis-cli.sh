#!/bin/bash

# TODO
# - refactor
# - make artemis-cli the main interface for all operations but split operation into
#  different bash scripts/aliases:
#   ./repos
#   ./grade w02h03 
#   ./grades scores

# contact
#   obermari PLUS pgdp AT cs DOT tum DOT edu
#   @ge36moy

#//////////////////////////////////////
#///////* CONFIGURATE HERE *///////////
#//////////////////////////////////////

# For a more pleasant experience save credentials by enabling the credentials storage in git
# $ git config --global credential.helper store

# Course settings
bitbucket='bitbucket.ase.in.tum.de'
course_name='pgdp1920'
course_id=37

# Don't redistribute without removing your credentials!
username="" # Your artemis username
password="" # Your artemis password

#//////////////////////////////////////
#//////////////////////////////////////

if [ -z "${username}" ] || [ -z "${password}" ]; then
  echo 'Enter your Artemis username and password into the script'
  exit 1
fi

# tum ids of students
declare -a students=(
  'solution' 'tests' 'exercise'
  # You can insert TUM IDs here or pass them seperated with spaces via the command line (commas are removed)
)

if [[ ! ($# -gt 0) ]]; then
  echo 'Usage: ./artemis-cli.sh assignment [tum_id1, ..., tum_idN] (e.g.: ./artemis-cli.sh w01h01 ge36moy, ge37moy, ge38moy)'
  exit 1
fi

if [[ $course_name -eq 'pgdp1920' && ! ($1 =~ ^w[0-9]+[hp][0-9]+$) ]]; then
  echo 'Assignment names in the PGdP course have to match w[0-9]+[hp][0-9]+'
  exit 1
fi

due_date=$(python3 detail/artemis_cli.py deadline $course_id $1 $username $password)

if [[ $? -ne 0 ]]; then
  exit 1
else
  echo "Checking out 'master@{deadline="$due_date"}'"
fi

for ((i = 2; i <= $#; i++ )); do
  student=$(echo ${!i} | sed 's/,//g')
  students+=("$student")
done

mkdir -p $1
cd $1

if [[ $? -ne 0 ]]; then
  echo -e "\e[91mFailed to create parent folder, check your permissions.\e[39m"
fi

touch scores
echo -e "#exercise:\"$1\"\n" > scores

cwd=$(pwd)

for i in "${students[@]}"
do
  echo -e "Fetching $i... \c"

  repo_local="$i"
  repo_remote="$course_name$1-$i"
  repo_url="https://$bitbucket/scm/$course_name$1/$repo_remote.git"

  {
    cd "$repo_local"
    git checkout master 1>/dev/null
    cd "$cwd"

    if ! git -C "$repo_local" pull --quiet && ! git clone --quiet "$repo_url" "$repo_local"; then
      echo -e "\e[91mfailed (1).\e[39m"
      continue
    fi

    cd "$repo_local"

    if [[ $? -eq 0 ]]; then
      echo -e "\e[92mok.\e[39m"
    else
      echo -e "\e[91mfailed.\e[39m"
      continue
    fi

    git log --sparse --full-history --all --pretty=format:"%an <%ae> %s%n%cn <%ce> %s" | grep -Ev '^(ArTEMiS <krusche\+artemis@in.tum.de|Erik Kynast <kynast@in.tum.de>|root <root@vmbruegge[0-9]*.informatik.tu-muenchen.de>)' > gitlog_mails

    if [ "$i" != "exercise" ] && [ "$i" != "solution" ] && [ "$i" != "tests" ]; then
      git checkout `git rev-list -1 --before="$due_date" master`
    fi

    git remote set-url --push origin forbidden
    cd "$cwd"
  } 2>/dev/null
done