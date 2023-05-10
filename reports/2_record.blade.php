@extends('layout.app')

@section('content')
    <ul class="nav nav-tabs" id="myTab" role="tablist">
        @foreach($infos as $key=>$info)
            <li class="nav-item {{$key==0?"active":""}}" role="presentation">
                <button class="nav-link fw-bold" id="home-tab-{{$info->id}}" data-bs-toggle="tab"
                        data-bs-target="#home-{{$info->id}}" type="button"
                        role="tab" aria-controls="home-{{$info->id}}" aria-selected="true">{{$info->name}}
                </button>
            </li>
        @endforeach

    </ul>
    <div class="tab-content" id="myTabContent">
        @foreach($infos as $key=>$info)
            <div class="tab-pane fade show {{$key==0?"active":""}}" id="home-{{$info->id}}" role="tabpanel"
                 aria-labelledby="home-tab-{{$info->id}}">
                <div class="m-4">
                    <h4 class="h4 text-muted fw-bolder text-center">Action Taken</h4>
                    <div
                            class="btn-group btn-group-lg col-lg-12"
                            role="group"
                            aria-label="Large button group"
                    >
                        @foreach($info->actions as $action)

                            <button type="button" class="btn btn-outline-dark">
                                {{$action->name}}
                            </button>

                        @endforeach
                    </div>

                    <h4 class="h4 text-muted fw-bold my-4 text-center">Target</h4>
                    <div
                            class="btn-group btn-group-lg col-lg-12"
                            role="group"
                            aria-label="Large button group"
                    >
                        @foreach($targets as $target)
                            <button type="button" class="btn btn-outline-dark">
                                {{$target->name}}
                            </button>
                        @endforeach
                    </div>

                    <h4 class="h4 text-muted fw-bold my-4  text-center fw-bold">Outcome</h4>
                    <div
                            class="btn-group btn-group-lg col-lg-12"
                            role="group"
                            aria-label="Large button group"
                    >
                        <button type="button" class="btn btn-success  fw-bold">
                            Success
                        </button>
                        <button type="button" class="btn btn-danger  fw-bold">
                            Failed
                        </button>
                        <button type="button" class="btn btn-warning  fw-bold">
                            Partial Success
                        </button>
                        <button type="button" class="btn btn-secondary  fw-bold">
                            Unknown
                        </button>
                    </div>
                </div>
            </div>
        @endforeach
    </div>
@endsection
<script>
    import FightRecorderComponent from "../js/components/FightRecorderComponent";

    export default {
        components: {FightRecorderComponent}
    }
</script>